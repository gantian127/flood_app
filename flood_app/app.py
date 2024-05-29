"""
This is the application for overland flow simulation

to test this app code:
from flood_app import create_app
app = create_app()
app.run(debug=True, port=5001)
"""

from flask import Flask, render_template, request, jsonify, send_file
from .model import FloodSimulator
import os

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import shutil


def create_app():
    app = Flask(__name__, template_folder="templates")

    # Route to render the HTML form
    @app.route("/")
    def index():
        return render_template("index.html")

    # Route to handle form submission
    @app.route("/run_model", methods=["POST"])
    def run_model():
        # Get user input text
        user_name = request.form["user_name"]
        if user_name == "":
            return jsonify({"error": "Please provide a valid user name."}), 400

        # make upload folder
        user_uploads = os.path.join(os.getcwd(), "user_uploads")
        if not os.path.isdir(user_uploads):
            os.mkdir(user_uploads)

        # make user folder
        user_folder = os.path.join(user_uploads, user_name)
        if not os.path.isdir(user_folder):
            os.mkdir(user_folder)

        # Check dem file
        if "dem_file" in request.files:
            dem_file = request.files["dem_file"]
            if dem_file.filename.endswith(".txt"):
                dem_file_path = os.path.join(user_folder, dem_file.filename)
                dem_file.save(dem_file_path)
            else:
                return jsonify({"error": "Please upload a valid dem file."}), 400

        # check config file
        if "config_file" in request.files:
            config_file = request.files["config_file"]
            if config_file.filename.endswith(".toml"):
                config_file_path = os.path.join(user_folder, config_file.filename)
                config_file.save(config_file_path)
            else:
                return (jsonify({"error": "Please provide a valid config file."}), 400)

        # create output folder
        output_folder = os.path.join(user_folder, "output")
        if os.path.isdir(output_folder):
            shutil.rmtree(output_folder)
        os.mkdir(output_folder)

        # get model parameters
        with open(config_file_path, mode="rb") as fp:
            args = tomllib.load(fp)
        args["terrain"]["grid_file"] = dem_file_path
        args["output"]["output_folder"] = output_folder

        # run model
        fs = FloodSimulator(**args)
        fs.run()

        # zip output files
        zip_file_path = os.path.join(user_folder, f"{user_name}_output")
        shutil.make_archive(zip_file_path, "zip", output_folder)

        return send_file(f"{zip_file_path}.zip", as_attachment=True)

    return app
