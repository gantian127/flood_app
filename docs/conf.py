import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(".."))

project = "Flood App"
copyright = f"{datetime.datetime.now().year}, CSDMS"
author = "Tian Gan"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_mock_imports = [
    "flask",
    "landlab",
    "rasterio",
    "tqdm",
    "toml",
    "tomllib",
    "tomli",
    "numpy",
    "pandas",
    "click",
    "cherrypy",
]

html_theme = "furo"
html_logo = "_static/logo.png"
html_title = "Flood App"

html_css_files = ["custom.css"]

templates_path = ["_templates"]
exclude_patterns = ["_build"]
