# Widgy Editor for Django

[![Build Status](https://travis-ci.org/fusionbox/django-widgy.png)](https://travis-ci.org/fusionbox/django-widgy)

Widgy is a content editor somewhat in the line of CKEditor.  It is not a WYSIWYG
editor though.  Widgy is more suited than CKEditor for editing pages, as in a
CMS because it allows you to edit specific parts of the page and those parts
know how to render themselves.  Whereas a WYSIWYG stores its data in HTML, Widgy
stores it in a Tree where each node can render itself.

## Data Model
A Widgy page is composed of Tree of Nodes.  A Node deals with structure.  It
defines where a component lives in the Tree.  The Tree does not deal with pages
like the page tree in Mezzanine, rather it deals with a hierarchy of components
to be rendered on a page.

Each Node has an associated Content.  While a Node concerns itself with
structure, Contents deal with the specific data of a component.  All Nodes are
instances of the same class, while each Content has a different type.  Only
certain Content types are allowed to be nested under each other (i.e. an Input
Content probably needs to be inside a Form Content and you probably don't want
anything inside of a Text Content).  Nodes will check the validity of their
content's relationship before moving.

### Example of a Tree
**Note:** Content types are in parentheses.

    Node (TwoColumnLayout)
    |
    +-- Node (MainBucket)
    |   |
    |   +-- Node (Text)
    |   |
    |   +-- Node (Image)
    |   |
    |   +-- Node (Text)
    |   |
    |   +-- Node (Form)
    |       |
    |       +-- Node (Input)
    |       |
    |       +-- Node (Checkboxes)
    |       |
    |       +-- Node (Input)
    |
    +-- Node (SidebarBucket)
        |
        +-- Node (CallToAction)

## Minimum Viable Proof of Concept
In order to prove that a Node-Tree-based content editor is a viable solution,
here is a list of features that we feel are absolutely necessary.  When we
finish this feature list, we have proved that Widgy is possible.

Working:

  - One layout
  - Text widget
  - Front-end rendering of all the widgets
  - Node reordering
  - Node re-rooting (moving a node up/down in the tree, from the left column to
    the right column, for example)
  - Delete widgets
  - Image widget with file upload, or some other widget that makes it seem like
    less of a toy
  - Creating a new ContentPage
  - Adding widgets by dragging from a thing full of options
  - Widgets from apps besides `widgy` (custom project widgets)
  - Admin chrome around the widgy editor
  - Editing of the [mezzanine] page metadata (title, published)
  - Nice drag and drop: retain the inside node offset (ask Gavin), snap into
    drop targets on mouseover.
  - Follow mouse on scroll while dragging.
  - Nicer compatibility (preerrors and aftererrors)

## Features required before we can show somebody else
These are the features that we need to be able to show people other than
developers.  When we finish this feature list, we can sell it to other people in
the company.

  - Designer magic wand.

## JavaScript

We use require.js to handle dependency management and to encourage code
modularity.  This helps a lot in development, but it also means that page loads
may be rather slow. Widgy comes with a require.js build profile to use with
`django-require`. To use it, install `django-require` and add to your
settings:

    REQUIRE_BUILD_PROFILE = 'widgy.build.js'
    REQUIRE_BASE_URL = 'widgy/js'
    STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'

This will automatically build the javascript bundle during `collectstatic`.
This will require either `node` or `rhino` to run r.js. `django-require` with
detect whichever one you have installed. `rhino` is nice because it can be
apt-got.

# testing

    make test
