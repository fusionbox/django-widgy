from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize_view(request, self)


class AuthorizedMixin(WidgyViewMixin):
    """
    Makes sure to call auth before doing anything.

    This class should not be used by RestView subclasses.  RestView already
    makes the call to auth, but conveniently wraps the errors to return them in
    JSON-encoded responses.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            self.auth(request, *args, **kwargs)
        except PermissionDenied:
            if request.user.is_authenticated():
                raise
            else:
                return redirect_to_login(request.get_full_path())
        else:
            return super(AuthorizedMixin, self).dispatch(request, *args, **kwargs)
