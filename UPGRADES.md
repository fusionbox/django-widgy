# Notes on attempting to upgrade to Python and Django

## Initial Premise

I thought we'd be able to go straight to Django 5.2 and Python 3.14,
but we're currently stuck at Django 4.2 and Python 3.12, pending
updates of the Mezzanine dependency.

We're going to start by ignoring everything in this repository except
what's required to load the basic Python packages, to start with, and
then run local tests. This means we're disregarding Github, and Tox,
and Javascript, and what's in the ./demo folder. The steps to success
should look like:

1. Have python3.12 available
2. Create a virtual environment
3. Install packages from pyproject.toml
4. `pytest`
5. Run the demo site: `python manage.py runserver` (admin login
   demo:demo)

None of that should error. Everything else is out of scope for now.

## Post-upgrade cleanups

* widgy_i18n I18NChild.language_code needs to be longer than max_length=2.
* sorl.thumbnail and django-filer thumbnail are redundant, amke some
  kind of decision there.
