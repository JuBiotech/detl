[![PyPI version](https://img.shields.io/pypi/v/detl)](https://pypi.org/project/detl)
[![pipeline](https://github.com/jubiotech/detl/workflows/pipeline/badge.svg)](https://github.com/jubiotech/detl/actions)
[![coverage](https://codecov.io/gh/jubiotech/detl/branch/main/graph/badge.svg)](https://codecov.io/gh/jubiotech/detl)
[![documentation](https://readthedocs.org/projects/detl/badge/?version=latest)](https://detl.readthedocs.io/en/latest/?badge=latest)


# detl
With `detl` you can analyze raw data export CSVs from DASware 4 or 5.

## Installation
`detl` is available on PyPI:

```shell
pip install detl
```

Visit [Releases](https://github.com/JuBiotech/detl/releases) to find the latest release notes.

## For Developers
To make changes to  `detl` you should install it in a dedicated Python environment.
1. clone it via `git clone https://github.com/jubiotech/detl`
2. `cd detl`
3. `pip install -e .` to install it into your (activated!) Python environment

Before making commits, please set up the `pre-commit` to automate the code style conventions:

```shell
pip install pre-commit
pre-commit install
```
