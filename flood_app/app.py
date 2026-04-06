"""
This is the application for overland flow simulation

to test this app code:
from flood_app import create_app
app = create_app()
app.run(debug=True, port=5001)
"""

import os
import shutil
import toml
import uuid
import threading
import traceback

from flask import Flask, render_template, request, jsonify, send_file, current_app
from .model import FloodSimulator
from .evaluation import ModelEvaluation
from .settings import API_KEY
from .utils import create_ascii_files_from_geojson


def create_app():
    app = Flask(__name__, template_folder="templates")

    # Display a simple index page to show the app is running.
    @app.route("/")
    def index():
        return render_template("simple_index.html")

    def run_simulation(user_folder):
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

            # zip output files
            output_folder = os.path.join(user_folder, "output")
            model_eval = ModelEvaluation(
                land_type_path=os.path.join(user_folder, "land_type.txt"),
                max_water_depth_path=os.path.join(output_folder, "max_water_depth.asc"),
                cum_result_path=os.path.join(output_folder, "cum_result_test.txt"),
                infil_result_path=os.path.join(output_folder, "infil_result.txt"),
                output_folder=output_folder,
            )
            model_eval.evaluate()
            shutil.make_archive(output_folder, "zip", output_folder)

            # update status as failed
            status = "complete"

        except Exception as e:
            # update status as failed
            tb = traceback.format_exc()
            status = f"failed. Error info: {e}\n{tb}"
            print(status)

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
            timeout = data.get("timeout", 300)
            model_intervention = data.get("modelIntervention", True)
            model_param = data.get("modelParameters")

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
            ascii_files = create_ascii_files_from_geojson(
                map_data,
                user_folder,
                geojson_str=True,
                delineation=True,
                intervention=model_intervention,
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

        # # create land type files using a template
        # land_type_template_path = os.path.join(
        #     current_app.root_path, "land_type_berm.txt"
        # )
        # land_type_file_path = os.path.join(user_folder, "land_type.txt")
        # shutil.copy(land_type_template_path, land_type_file_path)

        # create config file
        config_template_path = os.path.join(current_app.root_path, "config_file.toml")
        with open(config_template_path, mode="r") as fp:
            args = toml.load(fp)
        args["terrain"]["grid_file"] = ascii_files["elevation"]
        args["terrain"]["outlet_id"] = int(ascii_files["outlet_id"])
        args["output"]["output_folder"] = output_folder
        args["model_run"]["time_out"] = timeout

        args["infil_info"]["conductivity_file"] = ascii_files["conductivity"]
        args["olf_info"]["mannings_file"] = ascii_files["mannings_n"]

        if model_param is not None:
            args["model_run"]["model_run_time"] = model_param.get("modelRunTime", 200)
            args["model_run"]["storm_duration"] = model_param.get("stormDuration", 10)
            args["model_run"]["activate_inf"] = model_param.get(
                "activateInfiltration", True
            )
            args["olf_info"]["rain_intensity"] = model_param.get("rainIntensity", 59.2)
            args["olf_info"]["steep_slopes"] = model_param.get("steepSlopes", True)
            args["olf_info"]["mannings_n"] = model_param.get("manningsN", 0.03)
            args["olf_info"]["alpha"] = model_param.get("alpha", 0.7)

        config_file_path = os.path.join(user_folder, "config_file.toml")
        with open(config_file_path, "w") as config_file:
            toml.dump(args, config_file)

        # create status file
        status_file_path = os.path.join(user_folder, "status.txt")
        with open(status_file_path, "w") as status_file:
            status_file.write("wait in queue")

        # submit job
        thread = threading.Thread(target=run_simulation, args=(user_folder,))
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
