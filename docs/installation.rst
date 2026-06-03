Installation
============

Install Package
---------------

.. Stable Release
.. ~~~~~~~~~~~~~~
..
.. A stable release can be installed via pip:
..
.. .. code-block:: bash
..
..     pip install flood_app

.. From Source
.. ~~~~~~~~~~~

Clone the repository and install dependencies using conda, then install the
package in editable mode with pip:

.. code-block:: bash

    git clone https://github.com/gantian127/flood_app
    cd flood_app
    conda install --file=requirements.txt -c conda-forge
    pip install -e .

Configure API Key
-----------------

Before deploying, set the API key in ``flood_app/settings.py``.
Generate a new key with:

.. code-block:: python

    import secrets
    secrets.token_hex(32)

Start the Server
----------------

.. code-block:: bash

    start-app --port=80 --host=0.0.0.0

Look at the line containing `Serving on` to see what host and port the
server is running on. Alternatively, you can use the `--host` and `--port`
options to specify a specific host and port (`--help` for help).

Development Tools
-----------------------

`Nox <https://nox.thea.codes/>`_ is used to automate testing, linting, and
building the documentation. Install it with:

.. code-block:: bash

    pip install nox

Available sessions:

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Command
     - Description
     - Python versions
   * - ``nox -s test``
     - Run the test suite with coverage report
     - 3.11, 3.12, 3.13
   * - ``nox -s lint``
     - Run ruff linter and formatter check
     - default
   * - ``nox -s docs``
     - Build the Sphinx HTML documentation
     - default

To run all sessions:

.. code-block:: bash

    nox

To run a specific session:

.. code-block:: bash

    nox -s test
    nox -s lint
    nox -s docs

To run tests against a specific Python version:

.. code-block:: bash

    nox -s test-3.12


.. Requirements
.. ------------
..
.. - Python ≥ 3.11
.. - ``landlab==2.10.0`` (pinned; do not upgrade without testing)
.. - conda package manager

.. Docker (Optional)
.. -----------------
..
.. Build and run with Docker:
..
.. .. code-block:: bash
..
..     docker build . -t flood_app
..     docker run -it -p 80:80 flood_app
..
.. Or pull the pre-built image:
..
.. .. code-block:: bash
..
..     docker pull gantian127/flood_app:latest
..     docker run -it -p 80:80 gantian127/flood_app
