[![PyPI version](https://img.shields.io/pypi/v/detl)](https://pypi.org/project/detl)
[![pipeline](https://github.com/jubiotech/detl/workflows/pipeline/badge.svg)](https://github.com/jubiotech/detl/actions)
[![coverage](https://codecov.io/gh/jubiotech/detl/branch/main/graph/badge.svg)](https://codecov.io/gh/jubiotech/detl)
[![documentation](https://readthedocs.org/projects/detl/badge/?version=latest)](https://detl.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6939620.svg)](https://doi.org/10.5281/zenodo.6939620)

# detl
With `detl` you can analyze raw data export CSVs from DASware 4 or 5.

# Code Example

Create your `ddata` dictionary containing data for all vessels by using `detl.parse()`.

```python
ddata = detl.parse(
    pathlib.Path('v4_NT-WMB-2.Control.csv')
)
```

`ddata` returns data for the given reactor vessels 1 to 4:

```python
{1: <detl.core.ReactorData at 0x1d1f29421c8>,
 2: <detl.core.ReactorData at 0x1d1f3eccf88>,
 3: <detl.core.ReactorData at 0x1d1f3eccd08>,
 4: <detl.core.ReactorData at 0x1d1f3ee1408>}
 ```
Head over to the [example notebooks](https://github.com/JuBiotech/detl/tree/main/notebooks) for more detailed insights and further application examples.

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

# Usage and Citing
`detl` is licensed under the [GNU Affero General Public License v3.0](https://github.com/JuBiotech/detl/blob/main/LICENSE.md).

When using `detl` in your work, please cite the [corresponding software version](https://doi.org/10.5281/zenodo.6939620).

```bibtex
@software{detl,
  author       = {Michael Osthege and
                  Niklas Tenhaef and
                  Valentin Steier and
                  Alexander Reiter},
  title        = {detl: A Python package for processing of DASware raw data exports},
  month        = jul,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.6939621},
  url          = {https://doi.org/10.5281/zenodo.6939621}
}
```
