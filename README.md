# batterway

[![PyPI](https://img.shields.io/pypi/v/batterway.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/batterway.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/batterway)][pypi status]
[![License](https://img.shields.io/pypi/l/batterway)][license]

[![Read the documentation at https://batterway.readthedocs.io/](https://img.shields.io/readthedocs/batterway/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/simonvanlierde/batterway/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/simonvanlierde/batterway/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/batterway/
[read the docs]: https://batterway.readthedocs.io/
[tests]: https://github.com/simonvanlierde/batterway/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/simonvanlierde/batterway
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _batterway_ via [pip] from [PyPI]:

```console
$ pip install batterway
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [GPL 3.0 license][License],
_batterway_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://batterway.readthedocs.io/en/latest/usage.html
[License]: https://github.com/simonvanlierde/batterway/blob/main/LICENSE
[Contributor Guide]: https://github.com/simonvanlierde/batterway/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/simonvanlierde/batterway/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_batterway
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```