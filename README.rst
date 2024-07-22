Flood App
============

A web application for overland flow simulation using Landlab.

Quickstart
----------

Use `conda` to install the necessary requirements and `flood_app`,

.. code::

    $ git clone https://github.com/gantian127/flood_app
    $ cd flood_app
    $ conda install --file=requirements.txt -c conda-forge
    $ pip install .

Start the server,

.. code::

    $ start-app --port=80 --host=0.0.0.0

Look at the line containing `Serving on` to see what host and port the
server is running on. Alternatively, you can use the `--host` and `--port`
options to specify a specific host and port (`--help` for help).

Now you can open a web browser and go to http://0.0.0.0, which will show a
user interface to run the overland flow simulation.

.. image:: user_interface.png
  :width: 300
  :alt: user interface

You can download the example
`DEM file <https://github.com/gantian127/flood_app/blob/master/tests/test_files/geer_canyon.txt>`_
and `Config file <https://github.com/gantian127/flood_app/blob/master/tests/test_files/config_file.toml>`_ for testing.
The response will download a zip file which includes the model outputs. (Please note: the web browser may block the download of the zip file as an insecure file.)

Use Docker
------
**Option1: Build docker image with a Docker file**

To build a new docker image with a
`Docker file <https://github.com/gantian127/flood_app/blob/master/Dockerfile>`_
that will be a flood_app server,

.. code::

    docker build . -t flood_app


After building, run the server,

.. code::

    docker run -it -p 80:80 flood_app

**Option2: Pull docker image from the Docker Hub**

To pull the docker image that will be a flood_app server,

.. code::

    docker pull gantian127/flood_app:latest

After building, run the server,

.. code::

    docker run -it -p 80:80 gantian127/flood_app

Once running, you can open a web browser and go to http://0.0.0.0, which will show a
user interface to run the overland flow simulation.
