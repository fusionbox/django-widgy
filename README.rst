Widgy: Tree Editor for Django
=============================

.. image:: https://travis-ci.org/fusionbox/django-widgy.png?branch=master
   :target: http://travis-ci.org/fusionbox/django-widgy
   :alt: Build Status

Widgy is a content editor somewhat in the line of CKEditor. It is not a
WYSIWYG editor though. Widgy is more suited than CKEditor for editing
pages, as in a CMS because it allows you to edit specific parts of the
page and those parts know how to render themselves. Whereas a WYSIWYG
stores its data in HTML, Widgy stores it in a Tree where each node can
render itself.

Widgy is available under the Apache Version 2.0 license. Contribute on github.

Documentation
-------------

Read Widgy's documentation at http://docs.wid.gy.

Installation
------------

Install with pip. ::

    pip install django-widgy

When developing Widgy, it might be handy to clone the repository then install
it. ::

    git clone git://github.com/fusionbox/django-widgy
    cd django-widgy
    pip install -e .

Design Philosophy
-----------------

Read about Widgy's data model at
http://docs.wid.gy/en/latest/design/data-model.html.


Contributing
------------

There is a developers mailing list available at `widgy@fusionbox.com
<https://groups.google.com/a/fusionbox.com/forum/#!forum/widgy>`_

Running the Tests
^^^^^^^^^^^^^^^^^

::

    pip install -r requirements-test.txt
    make test

``make test`` will run both the JavaScript and Python tests. To test one
or the other, use ``make test-js`` or ``make test-py``.

::

    $ tox

``$ tox`` will run the full test suite across all of the supported versions of
Django and Python.

Coverage
********
Once coverage_ is installed (``pip install coverage``), the Makefile
has two commands to help report on code coverage. ::

    make coverage

will run the tests with coverage enabled and generate HTML coverage
files. ::

    make browser

will run the tests and open the coverage report in your web browser.

.. _coverage: http://nedbatchelder.com/code/coverage/
