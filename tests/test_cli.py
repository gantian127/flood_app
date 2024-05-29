"""
This is the command line interface to start a server for the app

$ flood_app --port=80 --host=0.0.0.0

"""

from click.testing import CliRunner

from flood_app.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "help" in result.output
