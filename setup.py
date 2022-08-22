import pathlib

import setuptools

__packagename__ = "detl"
ROOT = pathlib.Path(__file__).parent


def get_version():
    import os
    import re

    VERSIONFILE = os.path.join(__packagename__, "__init__.py")
    initfile_lines = open(VERSIONFILE, "rt").readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


__version__ = get_version()


setuptools.setup(
    name=__packagename__,
    packages=setuptools.find_packages(),  # this must be the same as the name above
    version=__version__,
    description="Package for parsing and transforming DASware raw data exports.",
    url="https://github.com/JuBiotech/detl",
    author="IBG-1",
    copyright="(c) 2022 Forschungszentrum Jülich GmbH",
    license="GNU Affero General Public License v3.0",
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    install_requires=open(pathlib.Path(ROOT, "requirements.txt")).readlines(),
)
