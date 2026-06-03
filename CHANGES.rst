Changelog
=========

All notable changes to this project are documented here.

0.3.0 (2026-06-03)
------------------

New Features
~~~~~~~~~~~~

- Added ``ModelEvaluation`` class in ``evaluation.py`` to compute flood area,
  damage cost, and investment NPV after each simulation.
- Added intervention counting within and outside the watershed in evaluation.
- Added NPV method for calculating intervention cost (berms and mulch).
- Added support for spatially distributed Manning's n and hydraulic conductivity
  via raster file inputs.
- Added watershed elevation output as JSON file.
- Added ``modelIntervention`` flag to ``POST /submit_simulation`` to enable or
  disable land-type interventions.
- Added concurrent simulation control via ``threading.Semaphore`` in ``app.py``.
- Added ``max_surface_water_depth_final.json`` output file.

Bug Fixes
~~~~~~~~~

- Fixed GeoJSON coordinate convention so that ``x`` maps to column index and
  ``y`` maps to row index.
- Fixed hydraulic conductivity and Manning's n array assignment for spatially
  distributed inputs.
- Fixed no-data areas in JSON outputs to use ``-9999``.

Other Changes
~~~~~~~~~~~~~

- Updated default rain intensity, storm duration, and model run time.
- Updated mulch conductivity values in ``utils.py``.
- Pinned ``landlab==2.10.0``.
- Added Sphinx documentation under ``docs/``.
- Added ``CITATION.cff`` and ``CREDITS.rst``.

0.2.0
-----

New Features
~~~~~~~~~~~~

- Added asynchronous simulation execution with background threading.
- Added ``GET /check_status/<uuid>`` endpoint to poll simulation status and
  download results.
- Added Bearer token authorization to ``POST /submit_simulation``.
- Added GeoJSON map data parsing via ``create_ascii_files_from_geojson()``
  in ``utils.py``.
- Added watershed delineation support.
- Added simulation timeout parameter.
- Added ``modelParameters`` override support in the request body.

Other Changes
~~~~~~~~~~~~~

- Added ``settings.py`` for API key configuration.
- Added ``config_file.toml`` template for per-run simulation parameters.
- Added simple index page at ``GET /``.

0.1.0
-----

- Initial release with basic overland flow simulation using Landlab
  ``OverlandFlow`` and ``SoilInfiltrationGreenAmpt`` components.
- Flask application with ``POST /submit_simulation`` endpoint.
- CherryPy WSGI server via ``start-app`` CLI entry point.
