import click
import os
import shutil
import subprocess

DEFAULT_PYTHON_VERSION = "3.6"
PYTHON_VERSIONS = ["3.6"]

ADDITIONAL_CORE_DEPS = [
    "numpy>=1.13.0",
    "scipy>=1.2.1",
    "networkx==2.4-1"
]


@click.group()
def cli():
    pass


python_version_option = click.option(
    '--python-version',
    default=DEFAULT_PYTHON_VERSION,
    type=click.Choice(PYTHON_VERSIONS),
    show_default=True,
    help="Python version for the environment")


@cli.command(name="install", help="Install the plugin and its dependencies")
@python_version_option
def install(python_version):
    env_name = get_env_name(python_version)

    returncode = subprocess.call([
        "edm", "install", "-e", env_name,
        "--yes"] + ADDITIONAL_CORE_DEPS)
    if returncode:
        raise click.ClickException("Error while installing EDM dependencies.")

    returncode = edm_run(env_name, ["pip", "install", "-e", "."])
    if returncode:
        raise click.ClickException("Error while installing the local package.")


@cli.command(help="Run the tests")
@python_version_option
def test(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(
        env_name, ["python", "-m", "unittest", "discover", "-v"])

    if returncode:
        raise click.ClickException("There were test failures.")


@cli.command(help="Run flake")
@python_version_option
def flake8(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(env_name, ["flake8", "."])
    if returncode:
        raise click.ClickException(
            "Flake8 exited with exit status {}".format(returncode))


@cli.command(help="Runs the coverage")
@python_version_option
def coverage(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(
        env_name, ["coverage", "run", "-m", "unittest", "discover"])
    if returncode:
        raise click.ClickException("There were test failures.")

    returncode = edm_run(
        env_name, ["coverage", "report"])
    if returncode:
        raise click.ClickException(
            "There were errors whilst reporting coverage.")


@cli.command(help="Builds the documentation")
@python_version_option
@click.option('--apidoc-only', is_flag=True, help="Only generate API doc.")
@click.option(
    '--html-only', is_flag=True,
    help="Only generate HTML documentation (requires API doc in source/api)."
)
def docs(python_version, apidoc_only, html_only):
    if apidoc_only and html_only:
        raise click.ClickException("Conflicting request in the invocation.")

    env_name = get_env_name(python_version)
    doc_api = os.path.abspath(os.path.join("doc", "source", "api"))
    package = os.path.abspath("surfactant_example")

    if not html_only:
        click.echo("Generating API doc")
        if os.path.exists(doc_api):
            shutil.rmtree(doc_api)
        returncode = edm_run(
            env_name, ['sphinx-apidoc', '-o', doc_api, package, '*tests*'])
        if returncode:
            raise click.ClickException(
                "There were errors while building the API docs.")

    if not apidoc_only:
        click.echo("Generating HTML")
        returncode = edm_run(env_name, ["make", "html"], cwd="doc")
        if returncode:
            raise click.ClickException(
                "There were errors while building HTML documentation.")


def get_env_name(python_version):
    return "force-py{}".format(remove_dot(python_version))


def remove_dot(python_version):
    return "".join(python_version.split('.'))


def edm_run(env_name, cmd, cwd=None):
    return subprocess.call(["edm", "run", "-e", env_name, "--"]+cmd, cwd=cwd)


if __name__ == "__main__":
    cli()
