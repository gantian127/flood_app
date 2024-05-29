import click

from flood_app.start import start
from flood_app._version import __version__


@click.command()
@click.version_option(version=__version__)
@click.option("-p", "--port", default=80, help="port to run on")
@click.option("--host", default="0.0.0.0", help="host IP address")
@click.option("--ssl-cert", default=None, help="path to host SSL certificate")
@click.option("--ssl-key", default=None, help="path to host SSL key")
@click.option("--ssl-chain", default=None, help="path to host SSL certificate chain")
@click.option("--silent", is_flag=True, help="only emit messages on error")
def main(host, port, ssl_cert, ssl_key, ssl_chain, silent):
    if not silent:
        click.secho("🚀 launching flood app on {0}:{1}".format(host, port))
    start(host, port, ssl_cert, ssl_key, ssl_chain)
