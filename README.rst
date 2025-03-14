Flood App
============

A web application for overland flow simulation using `Landlab <https://github.com/landlab/landlab>`_.

Installation
+++++++++++++

Use `conda` to install the necessary requirements and `flood_app`.
Please edit /flood_app/flood_app/settings.py file to define the API_KEY after
downloading the code.


.. code::

    $ git clone https://github.com/gantian127/flood_app
    $ cd flood_app
    $ conda install --file=requirements.txt -c conda-forge
    $ pip install .


.. code::

    $ start-app --port=80 --host=0.0.0.0

Look at the line containing `Serving on` to see what host and port the
server is running on. Alternatively, you can use the `--host` and `--port`
options to specify a specific host and port (`--help` for help).

.. This is comments
    Opt.2 Use Docker
    ----------------
    **Method 1: Build docker image with a Docker file**
    To build a new docker image with a
    `Docker file <https://github.com/gantian127/flood_app/blob/master/Dockerfile>`_
    that will be a flood_app server,
    .. code::
        docker build . -t flood_app
    After building, run the server,
    .. code::
        docker run -it -p 80:80 flood_app
    **Method 2: Pull docker image from the Docker Hub**
    To pull the docker image that will be a flood_app server,
    .. code::
        docker pull gantian127/flood_app:latest
    After building, run the server,
    .. code::
        docker run -it -p 80:80 gantian127/flood_app
    Once running, you can open a web browser and go to http://0.0.0.0, which will show a
    user interface to run the overland flow simulation.
..

API Specification
+++++++++++++++++
This API allows users to submit and check the status of overland flow simulations.

Endpoints
---------
**1. Submit Simulation**

**URL:** POST /submit_simulation

**Description:** Submit request for a new overland flow simulation.


**Request Headers:**

.. code::

    Authorization: Bearer API_KEY
    Content-Type: application/json

**Request Body:**

.. code::

    {
      "map": {map_json_string},
      "simulationId": "uuid",
      "timeout": 300
    }

    Content-Type: application/json

**Responses:**

- ✅ 200 OK – Simulation received
- ❌ 400 Bad Request – Missing or invalid parameters
- ❌ 401 Unauthorized – API key missing or incorrect
- ❌ 403 Forbidden – Invalid API key

**Example:**

.. code::

    curl -X POST "http://0.0.0.0/submit_simulation" \
         -H "Authorization: Bearer API_KEY_as_64-character_hex_string" \
         -H "Content-Type: application/json" \
         -d @example_request.json

- See example_request.json at ./tests/data/test_request_json_valid.json


**2. Check Simulation Status**

**URL:** GET /check_status/{simulation_id}

**Description:** Check the current status of a simulation.

**Responses:**

- ✅ 200 OK – Simulation is complete or processing
- ❌ 400 Bad Request – Simulation ID is invalid or not found
- ❌ 500 Internal Server error – Simulation is failed

**Example:**

.. code::

    # check status only
    curl "http://0.0.0.0/check_status/2f144dc1-25a6-484f-91d0-42ddb0ef75bb"

    # download file
    curl "http://0.0.0.0/check_status/2f144dc1-25a6-484f-91d0-42ddb0ef75bb?download=true" \
          --output /local_path/output.zip
