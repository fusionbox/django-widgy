# Notes on attempting to upgrade to Python 3.14 and Django 5.2

## Initial Premise

We're going to start by ignoring everything in this repository except
what's required to load the basic Python packages, to start with, and
then run local tests. This means we're disregarding Github, and Tox,
and Javascript, and what's in the ./demo folder. The steps to success
should look like:

1. Have python3.14 available
2. Create a virtual environment
3. Install packages from pyproject.toml
4. `pytest`

None of that should error. Everything else is out of scope for now.
