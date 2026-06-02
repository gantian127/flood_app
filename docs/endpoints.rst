API Documentation
=================

This API allows users to submit and check the status of model simulations.

Submit Simulation
-----------------

**URL:** POST /submit_simulation

**Description:** Submit request for a new model simulation.

**Request Headers**

.. code-block::

    Authorization: Bearer API_KEY
    Content-Type: application/json

**Request Body**

.. code-block::

    {
      "map": {map_json_string},
      "simulationId": "uuid",
      "timeout": 300
    }

    Content-Type: application/json

**Responses**

- ✅ 200 OK – Simulation received
- ❌ 400 Bad Request – Missing or invalid parameters
- ❌ 401 Unauthorized – API key missing or incorrect
- ❌ 403 Forbidden – Invalid API key

**Example**

.. code-block::

    curl -X POST "http://0.0.0.0/submit_simulation" \
         -H "Authorization: Bearer API_KEY_as_64-character_hex_string" \
         -H "Content-Type: application/json" \
         -d @example_request.json

An example JSON file for ``example_request.json`` can be found in
:download:`test_request_geojson_valid.json <../tests/data/test_request_geojson_valid.json>`.

Check Simulation Status
-----------------------

**URL:** GET /check_status/{simulation_id}

**Description:** Check the current status of a simulation.

**Responses**

- ✅ 200 OK – Simulation is complete or processing
- ❌ 400 Bad Request – Simulation ID is invalid or not found
- ❌ 500 Internal Server error – Simulation is failed

**Example**

.. code-block::

    # check status only
    curl "http://0.0.0.0/check_status/2f144dc1-25a6-484f-91d0-42ddb0ef75bb"

    # download file
    curl "http://0.0.0.0/check_status/2f144dc1-25a6-484f-91d0-42ddb0ef75bb?download=true" \
          --output /local_path/output.zip