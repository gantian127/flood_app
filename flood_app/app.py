"""
This is the application for overland flow simulation

to test this app code:
from flood_app import create_app
app = create_app()
app.run(debug=True, port=5001)
"""

import os
import time
import shutil
import toml
import uuid
import threading

from flask import Flask, request, jsonify, send_file, current_app
from .model import FloodSimulator
from .settings import API_KEY
from .utils import create_ascii_files


def create_app():
    app = Flask(__name__, template_folder="templates")

    def run_simulation(user_folder, time_out):
        # Record the start time for timeout checking
        start_time = time.time()

        # update status as processing
        status_file_path = os.path.join(user_folder, "status.txt")
        with open(status_file_path, "w") as status_file:
            status_file.write("processing")

        # get model parameters
        config_file_path = os.path.join(user_folder, "config_file.toml")
        with open(config_file_path, mode="r") as fp:
            args = toml.load(fp)

        try:
            # run model
            fs = FloodSimulator(**args)
            fs.run()

            # Check if time has exceeded timeout
            if time.time() - start_time > time_out:
                error_info = f"Simulation timeout exceeded {time_out} sec."
                raise Exception(error_info)

            # zip output files
            output_folder = os.path.join(user_folder, "output")
            zip_file_path = os.path.join(user_folder, "output")
            shutil.make_archive(zip_file_path, "zip", output_folder)

            # update status as failed
            status = "complete"

        except Exception as e:
            # update status as failed
            status = f"failed. Error info: {e}"

        finally:
            # update the status file, whether success or failure
            status_file_path = os.path.join(user_folder, "status.txt")
            with open(status_file_path, "w") as status_file:
                status_file.write(status)

        return

    # Route to handle submission
    @app.route("/submit_simulation", methods=["POST"])
    def submit_simulation():
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        api_key = auth_header.split("Bearer ")[1]
        if api_key != API_KEY:
            return jsonify({"error": "Invalid API Key"}), 403

        # parse JSON data
        try:
            data = request.get_json()
            map_data = data.get("map")
            simulation_id = data.get("simulationId")
            timeout = data.get("timeout")

            # check map data
            if not map_data:
                return jsonify({"error": "Missing valid map data."}), 400

            # check simulation id
            try:
                uuid.UUID(simulation_id, version=4)
            except ValueError:
                return jsonify({"error": "Please provide a valid simulation ID."}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # prepare simulation folder
        # make upload folder
        user_uploads = os.path.abspath(
            os.path.join(current_app.root_path, "..", "user_upload")
        )
        if not os.path.isdir(user_uploads):
            os.mkdir(user_uploads)

        # make user folder
        user_folder = os.path.join(user_uploads, simulation_id)
        if os.path.isdir(user_folder):
            return (
                jsonify(
                    {
                        "error": f"Request {simulation_id} is rejected. "
                        f"Simulation ID already exists."
                    }
                ),
                400,
            )
        os.mkdir(user_folder)

        # create output folder
        output_folder = os.path.join(user_folder, "output")
        if os.path.isdir(output_folder):
            shutil.rmtree(output_folder)
        os.mkdir(output_folder)

        # create ascii files
        try:
            dem_ascii_path, mannings_ascii_path = create_ascii_files(
                map_data,
                user_folder,
                json_str=True,
                delineation=False,
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "error": f"Request {simulation_id} is rejected. "
                        f"Invalid map json string: {e}"
                    }
                ),
                400,
            )

        # create config file
        config_template_path = os.path.join(current_app.root_path, "config_file.toml")
        with open(config_template_path, mode="r") as fp:
            args = toml.load(fp)
        args["terrain"]["grid_file"] = dem_ascii_path
        args["output"]["output_folder"] = output_folder

        config_file_path = os.path.join(user_folder, "config_file.toml")
        with open(config_file_path, "w") as config_file:
            toml.dump(args, config_file)

        # create status file
        status_file_path = os.path.join(user_folder, "status.txt")
        with open(status_file_path, "w") as status_file:
            status_file.write("wait in queue")

        # submit job
        thread = threading.Thread(target=run_simulation, args=(user_folder, timeout))
        thread.start()

        return jsonify({"message": f"Request {simulation_id} is received."}), 200

    @app.route("/check_status/<simulation_id>", methods=["GET"])
    def check_status(simulation_id):
        """API to check the model run status"""

        # check simulation id
        try:
            uuid.UUID(simulation_id, version=4)
        except ValueError:
            return jsonify({"error": "Please provide a valid simulation ID."}), 400

        # check status of simulation
        user_uploads = os.path.abspath(
            os.path.join(current_app.root_path, "..", "user_upload")
        )
        user_folder = os.path.join(user_uploads, simulation_id)

        if os.path.isdir(user_folder):
            status_file_path = os.path.join(user_folder, "status.txt")
            with open(status_file_path, "r") as f:
                status = f.read()

            if status in ["waiting in queue", "processing"]:
                return (
                    jsonify({"message": f"Request {simulation_id} is {status}."}),
                    200,
                )
            elif "failed" in status:
                return jsonify({"error": f"Request {simulation_id} is {status}"}), 500
            elif status == "complete":
                zip_output_path = os.path.join(user_folder, "output.zip")
                if os.path.isfile(zip_output_path):
                    download = request.args.get("download", "false").lower() == "true"
                    if download:
                        return send_file(f"{zip_output_path}", as_attachment=True)
                    else:
                        return (
                            jsonify(
                                {"message": f"Request {simulation_id} is complete."}
                            ),
                            200,
                        )

        else:
            return jsonify({"error": "Simulation ID not found."}), 400

    return app
