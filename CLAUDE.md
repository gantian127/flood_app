# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flood App is a RESTful web service that runs overland flow simulations using [Landlab](https://github.com/landlab/landlab). It accepts GeoJSON map data via a POST endpoint, runs the simulation asynchronously using Python threads, and returns results as a zipped archive.

## Installation

```bash
conda install --file=requirements.txt -c conda-forge
pip install -e .
```

Requires Python ≥ 3.11 and `landlab==2.10.0` (pinned; do not upgrade without testing).

## Common Commands

```bash
# Start the server
start-app --port=80 --host=0.0.0.0

# Run all tests (includes doctests in source modules)
pytest

# Run a single test file
pytest tests/test_app.py

# Run a single test by name
pytest tests/test_app.py::test_submit_simulation_valid_requests

# Run linter
flake8 flood_app tests

# Sort imports
isort flood_app tests
```

## Architecture

### Request Lifecycle

1. `POST /submit_simulation` in `app.py` — validates API key, parses GeoJSON, calls `create_ascii_files_from_geojson()` (in `utils.py`) to produce `.txt` ASCII grid files, writes a `config_file.toml`, and spawns a background thread.
2. The thread runs `FloodSimulator` (`model.py`) then `ModelEvaluation` (`evaluation.py`), writes a status file, and zips the output.
3. `GET /check_status/<uuid>` reads the status file and, when complete, can stream the zip as a download.

Concurrency is serialized by a single `threading.Semaphore(1)` in `app.py:33` — only one simulation runs at a time; others queue up.

### Key Modules

| File | Role |
|---|---|
| `app.py` | Flask factory (`create_app`), route handlers, threading logic |
| `model.py` | `FloodSimulator` — wraps Landlab `OverlandFlow` + `SoilInfiltrationGreenAmpt` |
| `evaluation.py` | `ModelEvaluation` — post-run analysis: flood area, damage cost, investment NPV |
| `utils.py` | GeoJSON → ESRI ASCII conversion; `watershed_delineation`; `calculate_npv` |
| `cli.py` | Click entry point (`start-app`), delegates to `start.py` |
| `start.py` | CherryPy WSGI host wrapping the Flask app |
| `settings.py` | `API_KEY` — edit this file to set the key before deploying |

### Configuration

`flood_app/config_file.toml` is the template for every run. At request time `app.py` copies it, injects per-request paths (`grid_file`, `outlet_id`, etc.) and optional `modelParameters` overrides, then writes it to the simulation's folder in `user_upload/<uuid>/`.

### GeoJSON Coordinate Convention

The GeoJSON `features[i].properties.x` means **column index** and `.y` means **row index** — the opposite of the usual (x=east, y=north) convention. This is intentional and matches the upstream platform format. Do not swap them.

### Land-type Interventions

`utils.py` defines three intervention types applied during GeoJSON parsing:
- `berm_low` — raises elevation by 1 m
- `berm_high` — raises elevation by 2 m
- `mulch` — changes conductivity only (no elevation change)

These map to entries in `MANNING_MAPPING`, `CONDUCTIVITY_MAPPING`, and `LANDTYPE_MAPPING`.

### Output Files (per simulation, under `user_upload/<uuid>/output/`)

| File | Contents |
|---|---|
| `surface_water_depth_<t>.json` | Per-timestep water depth grid |
| `infiltration_<t>.json` | Per-timestep infiltration depth grid |
| `max_water_depth.asc` / `max_surface_water_depth_final.json` | Maximum water depth over entire run |
| `watershed_elevation.json` | Elevation grid of delineated watershed |
| `outlet_discharge.csv` | Time series of outlet discharge |
| `cum_result_test.txt` / `infil_result.txt` | Scalar summary percentages |
| `evaluation_results.txt` | Damage cost, flooded area, investment NPV |

## Testing

Tests live in `tests/` and use `pytest-datadir` — test fixture JSON files are in `tests/data/`. The `shared_datadir` fixture resolves to that directory.

The full test suite includes doctests (`--doctest-modules` in `pyproject.toml`); any public function with a doctest must keep it passing.

`test_check_status_timeout_id` sleeps for 60 s and is skipped on Windows.

## API Key

The key is hardcoded in `flood_app/settings.py`. Generate a new one with:
```python
import secrets; secrets.token_hex(32)
```

# Commit Guidelines

- Use Conventional Commits.
- Separate code changes and documentation changes into different commits.
- Do not include co-author attribution.
- Keep commit subjects concise and descriptive.
