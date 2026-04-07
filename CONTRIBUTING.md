# Contributing

## Local development

The following tools must be available on your system
to set up a development environment:

- `make`
- [Python]
- [uv]

[Python]: https://www.python.org/downloads/
[uv]: https://docs.astral.sh/uv/

### Creating a virtual environment

Ensure one of the supported Pythons (see README) is installed and used by the `python` executable:

```sh
python3 --version
```

Then create and activate a virtual environment. If you don't have any other way of managing virtual
environments this can be done by running:

```sh
make install
source .venv/bin/activate
```

### Install PostgreSQL

Ensure that a supported version of PostgreSQL (see README) is installed and running on your local machine.

### Installing Python dependencies

To install all the development dependencies in your virtual environment, run:

```sh
make install
```

[direnv]: https://direnv.net
[virtualenvwrapper]: https://virtualenvwrapper.readthedocs.io/

### Testing

To start the tests with [tox], run:

```sh
make test
```

Alternatively, if you want to run the tests directly in your virtual environment,
you many run the tests with:

```sh
PYTHONPATH=src python3 -m pytest
```

### Static analysis

Run all static analysis tools with:

```sh
make lint
```

### Managing dependencies

Package dependencies are declared in `pyproject.toml`.

- _package_ dependencies in the `dependencies` array in the `[project]` section.
- _development_ dependencies in the `dev` array in the `[project.optional-dependencies]` section.

For local development, the dependencies declared in `pyproject.toml` are pinned to specific
versions using the `uv.lock` lock file.
You should not manually edit the `uv.lock` lock file.


#### Adding a new dependency

To install a new Python dependency add it to the appropriate section in `pyproject.toml` and then
run:

```sh
make install
```

This will:

1. Build a new version of the `uv.lock` lock file containing the newly added
   package.
2. Sync your installed packages with those pinned in `uv.lock`.

This will not change the pinned versions of any packages already in the lock file unless
needed by the new packages, even if there are updated versions of those packages available.

Remember to commit your changed `uv.lock` files alongside the changed
`pyproject.toml`.

#### Removing a dependency

Removing Python dependencies works exactly the same way: edit `pyproject.toml` and then run
`make install`.

#### Updating all Python packages

To update the pinned versions of all packages run:

```sh
make update
```

This will update the pinned versions of every package in the `uv.lock` lock
file to the latest version which is compatible with the constraints in `pyproject.toml`.

You can then run:

```sh
make install
```

to sync your installed packages with the updated versions pinned in `uv.lock`.

#### Updating individual Python packages

Upgrade a single development dependency with:

```sh
uv lock -P $PACKAGE==$VERSION --resolver=backtracking
```

You can then run:

```sh
make install
```

to sync your installed packages with the updated versions pinned in `uv.lock`.

[tox]: https://tox.wiki
