import os
from setuptools import setup, find_packages

VERSION = "0.1.0.dev0"


# Read description
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()


def write_version_py():
    filename = os.path.join(
        os.path.dirname(__file__),
        'surfactant_example',
        'version.py')
    ver = "__version__ = '{}'\n"
    with open(filename, 'w') as fh:
        fh.write(ver.format(VERSION))


write_version_py()

setup(
    name="surfactant_example",
    version=VERSION,
    entry_points={
        "force.bdss.extensions": [
            "surfactant_example = "
            "surfactant_example.surfactant_plugin:SurfactantPlugin",
        ]
    },
    packages=find_packages(),
    install_requires=[
        "force_bdss >= 0.5.0",
        "force_wfmanager >= 0.5.0",
        "force_gromacs >= 0.1.0.dev0",
    ]
)
