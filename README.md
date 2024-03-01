# Django Integrity

Django Integrity contains tools for controlling deferred constraints
and handling `IntegrityError`s in Django projects which use PostgreSQL.

## Supported dependencies

This package is tested against:

- Python 3.10, 3.11, or 3.12.
- Django 4.1, 4.2, or 5.0.
- PostgreSQL 12 to 16
- psycopg2 and psycopg3

## Local development

### Creating a virtual environment

Ensure one of the above Pythons is installed and used by the `python` executable:

```sh
python --version
```

Then create and activate a virtual environment. If you don't have any other way of managing virtual
environments this can be done by running:

```sh
python -m venv .venv
source .venv/bin/activate
```

You could also use [virtualenvwrapper], [direnv] or any similar tool to help manage your virtual
environments.

### Install PostgreSQL

Ensure that PostgreSQL with minimum version 12 is installed and running on your local machine. 

### Installing Python dependencies

> [!NOTE]
> You might not need to install the below requirements if you only intend to run the tests,
> because we use [tox] for the tests, and it manages the installation of dependencies.

If you only intend to run the tests with [tox], then you may only require:

```sh
pip install tox
```

Alternatively, to install all the development dependencies in your virtual environment, run:

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
python -m pytest
```

### Static analysis

Run all static analysis tools with:

```sh
make lint
```

This may make changes to the local files if improvements are available.

### Managing dependencies

Package dependencies are declared in `pyproject.toml`.

- _package_ dependencies in the `dependencies` array in the `[project]` section.
- _development_ dependencies in the `dev` array in the `[project.optional-dependencies]` section.

For local development, the dependencies declared in `pyproject.toml` are pinned to specific
versions using the `requirements/development.txt` lock file.
You should not manually edit the `requirements/development.txt` lock file.

Prerequisites for installing those dependencies are tracked in the `requirements/prerequisites.txt`.


#### Adding a new dependency

To install a new Python dependency add it to the appropriate section in `pyproject.toml` and then
run:

```sh
make install
```

This will:

1. Build a new version of the `requirements/development.txt` lock file containing the newly added
   package.
2. Sync your installed packages with those pinned in `requirements/development.txt`.

This will not change the pinned versions of any packages already in any requirements file unless
needed by the new packages, even if there are updated versions of those packages available.

Remember to commit your changed `requirements/development.txt` files alongside the changed
`pyproject.toml`.

#### Removing a dependency

Removing Python dependencies works exactly the same way: edit `pyproject.toml` and then run
`make install`.

#### Updating all Python packages

To update the pinned versions of all packages run:

```sh
make update
```

This will update the pinned versions of every package in the `requirements/development.txt` lock
file to the latest version which is compatible with the constraints in `pyproject.toml`.

You can then run:

```sh
make install
```

to sync your installed packages with the updated versions pinned in `requirements/development.txt`.

#### Updating individual Python packages

Upgrade a single development dependency with:

```sh
pip-compile -P $PACKAGE==$VERSION pyproject.toml --resolver=backtracking --extra=dev --output-file=requirements/development.txt
```

You can then run:

```sh
make install
```

to sync your installed packages with the updated versions pinned in `requirements/development.txt`.

[tox]: https://tox.wiki
