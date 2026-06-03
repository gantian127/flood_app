import nox

PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    """Run the test suite."""
    session.install("-e", ".[testing]")
    session.run(
        "pytest",
        "--cov=flood_app",
        "--cov-report=term-missing",
    )


@nox.session
def lint(session):
    """Run linting and formatting."""
    session.install("ruff")
    session.run("ruff", "check", "flood_app", "tests", "--fix")
    session.run("ruff", "format", "flood_app", "tests")


@nox.session
def docs(session):
    """Build the Sphinx documentation."""
    session.install("-r", "docs/requirements.txt")
    session.install("-e", ".")
    session.run("sphinx-build", "-M", "html", "docs", "docs/_build", "-W")
