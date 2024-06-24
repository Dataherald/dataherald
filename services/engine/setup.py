"""Set up the package."""

import os
from pathlib import Path

from setuptools import find_packages, setup

DEFAULT_PACKAGE_NAME = "dataherald"
PACKAGE_NAME = os.environ.get("PACKAGE_NAME_OVERRIDE", DEFAULT_PACKAGE_NAME)

# with open(Path(__file__).absolute().parents[0] / "dataherald" / "VERSION") as _f:
#     __version__ = _f.read().strip()  # noqa: ERA001
__version__ = "0.0.1"

with open(Path(__file__).absolute().parents[0] / "README.md", encoding="utf-8") as f:
    long_description = f.read()

install_requires = []


setup(
    author="Amir Zohrenejad",
    name=PACKAGE_NAME,
    version=__version__,
    packages=find_packages(),
    description="text-to-sql engine for question answering over structured data",
    install_requires=install_requires,
    long_description=long_description,
    license="",  # need to be added
    url="https://github.com/Dataherald/dataherald",
    include_package_data=True,
    long_description_content_type="text/markdown",
)
