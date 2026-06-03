.. image:: docs/_static/Logo.png
    :alt: Flood App logo
    :width: 400px
    :align: center

.. image:: https://img.shields.io/badge/docs-GitHub%20Pages-blue
    :target: https://gantian127.github.io/flood_app/
    :alt: Documentation

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT

.. .. image:: https://readthedocs.org/projects/flood-app/badge/?version=latest
..    :target: https://flood-app.readthedocs.io/en/latest/?badge=latest
..    :alt: Documentation Status

.. .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.18475558.svg
..     :target: https://doi.org/10.5281/zenodo.18475558
..     :alt: DOI

Flood App is a RESTful web service that integrates with the
`Fora.ai platform <https://fora.northeastern.edu/>`_ to support participatory
watershed modeling. Built on `Landlab <https://landlab.csdms.io/>`_, the service
performs watershed-scale simulations of surface runoff and soil infiltration based
on user-defined landscape conditions and mitigation interventions.

Community users interact through the Fora.ai platform to design modeling scenarios
that incorporate mitigation measures such as berms and mulch. Fora.ai sends
GeoJSON-based map data to Flood App through a REST API, where the inputs are
translated into physics-based simulations using Landlab components. Simulations are
executed asynchronously and the results are returned to Fora.ai for visualization,
scenario comparison, and decision support.

Installation
------------

Clone the repository, install dependencies with conda, then install the package:

.. code-block:: bash

    git clone https://github.com/gantian127/flood_app
    cd flood_app
    conda install --file=requirements.txt -c conda-forge
    pip install -e .

Start the server:

.. code-block:: bash

    start-app --port=80 --host=0.0.0.0

Documentation
-------------

Please read the `Full documentation <https://flood-app.readthedocs.io>`_ on ReadTheDocs
for detailed information about Flood App.


API Specification
-----------------

For the API specification including request/response formats and examples,
see the `API Documentation <https://flood-app.readthedocs.io/en/latest/endpoints.html>`_.

Contributing
------------

Contributions are welcome! Please read
`CONTRIBUTING <https://github.com/gantian127/flood_app/blob/master/CONTRIBUTING.rst>`_
for guidelines on reporting issues and submitting pull requests.

License
-------

MIT — see
`LICENSE <https://github.com/gantian127/flood_app/blob/master/LICENSE.rst>`_
for details.

Citation
--------

If you use Flood App in your research, please cite it using the metadata in
`CITATION.cff <https://github.com/gantian127/flood_app/blob/master/CITATION.cff>`_
or via the GitHub "Cite this repository" button.

Credits
-------

See `CREDITS <https://github.com/gantian127/flood_app/blob/master/CREDITS.rst>`_
for the list of contributors and acknowledgments.
