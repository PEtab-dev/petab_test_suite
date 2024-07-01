"""PEtab test suite python package"""

from setuptools import setup, find_namespace_packages
from os import path

here = path.abspath(path.dirname(__file__))


def read(fname):
    with open(fname, encoding="utf-8") as f:
        return f.read()


# Get the long description from the README file
long_description = read(path.join(here, "README.md"))

# Get the version
exec(read(path.join(here, "petabtests", "version.py")))

setup(
    version=__version__,  # noqa: F821
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(),
    include_package_data=True,
)
