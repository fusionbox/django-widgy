Widgy: Tree Editor for Django
=============================

.. image:: https://travis-ci.org/fusionbox/django-widgy.png
   :target: http://travis-ci.org/fusionbox/django-widgy
   :alt: Build Status

Widgy is a content editor somewhat in the line of CKEditor. It is not a
WYSIWYG editor though. Widgy is more suited than CKEditor for editing
pages, as in a CMS because it allows you to edit specific parts of the
page and those parts know how to render themselves. Whereas a WYSIWYG
stores its data in HTML, Widgy stores it in a Tree where each node can
render itself.

Widgy is available under the 2-clause BSD license. Contribute on github.

Documentation
-------------

Read Widgy's documentation at http://django-widgy.readthedocs.org.

Installation
------------

Widgy does not yet have a stable release, so it should be installed from
source. ::

    pip install -e git://github.com/fusionbox/django-widgy#egg=widgy

When developing Widgy, it might be handy to clone the repository then install
it. ::

    git clone git://github.com/fusionbox/django-widgy
    cd django-widgy
    pip install -e .

Design Philosophy
-----------------

Read about Widgy's data model at
http://django-widgy.readthedocs.org/en/latest/design/data-model.html.

Running the Tests
-----------------

::

    make test

``make test`` will run both the JavaScript and Python tests. To test one
or the other, use ``make test-js`` or ``make test-py``.

Coverage
^^^^^^^^
Once coverage_ is installed (``pip install coverage``), the Makefile
has two commands to help report on code coverage. ::

    make coverage-py

will run the tests with coverage enabled and generate HTML coverage
files. ::

    make browser-py

will run the tests and open the coverage report in your web browser.

You can also run the JavaScript coverage by first installing node-jscoverage_
and then running::

    make coverage-js

This will output a coverage report in js_tests/coverage.html.  You can open
that file using::

    make browser-js

Like ``make test``, ``make coverage`` (and ``make browser``) will run both the
Python and JavaScript coverage commands.

.. _coverage: http://nedbatchelder.com/code/coverage/

.. _node-jscoverage: https://github.com/visionmedia/node-jscoverage
