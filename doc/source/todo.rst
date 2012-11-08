Things left to do
=================

Tasks and todo items should be listed here and organized.


Implementation Tasks
====================
- Fork ``filebrowser`` application to use file objects.

      ``Filebrowser`` does not store objects in the database.  The CMS needs to be
      able to attach relationships to files and cannot do so until the application
      is forked to use relational models instead of directly looking at the file
      system for browsing, adding, updating, deleting, and viewing.

- Page linking

      When pages are linked together through anchor tags, there needs to be a way
      to update these links if there are URL changes made to the page that was
      being linked to.  For example:

      Page A has a reference to Page B.  Page B updates its URL and schedules the
      change.  When Page B is published, Page A needs to automatically update its
      reference to the new URL.


Functional Requirement Tasks
============================
- Text Replacements

      Admin users can add a list of ``{word} => {replacement}`` mappings.  Every
      time the ``word`` is encountered on the frontend, it will be replaced with
      the text ``replacement``.

- Page versioning

   - Each page needs to maintain many versions of itself.
   - Versions can be selecting for display on the frontend and may be reverted
     to a previous version.
   - Any page version can be viewed as it would look if it were to be reverted.

- Page publishing

      A version of a page (see above) can be scheduled for publishing 


Usability Concerns
==================
- A few ``WidgyField`` field widget changes need to be made.

   1. Full width

   2. Better represent the output on the page (example: columns need to display
         side by side, not underneath like rows)

   3. Each editor needs a usability overview

   4. Each content template needs a usability overview

   5. Drag, drop, hover, and other visual cues need a usablity overview.

- API issues

      Validation and forms should only have to be written once.


Source Code TODOs
=================
.. todolist::
