import click
import subprocess
import os

@click.group()
def cli():
    ...


@cli.command()
def deploy():
    click.echo("Running chalice deploy")
    output = subprocess.check_output(f"source {os.environ['VIRTUAL_ENV']}/bin/activate && chalice deploy",shell=True)
    click.echo(output)
    click.echo(os.environ["VIRTUAL_ENV"])


