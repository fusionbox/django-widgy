# Stuff

- Remove mezanine.
- Replace urlconf with middleware.
- Figure out compatibility with page\_builder `Layout` classes.

# Features

- Undelete Page
- Leaving redirects behind correctly.
- Tests

# Notes

The base code for site\_builder is pretty strait forward.  The biggest issue
I'm running into is much of the code seems to be dependent on what
implementation of 'admin' a user takes.  If you are using the build in
`django.contrib.admin` then all will go fine.  However, how do I write this in
such a way that allows you to write your own interface for page editing and not
end up having to re-implement everything...
