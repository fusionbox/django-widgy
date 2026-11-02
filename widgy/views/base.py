import json

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from django.views.generic import View


class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize_view(request, self)


class RestView(View):
    """
    Base class for JSON API views.

    Calls ``auth`` before dispatching, parses a JSON request body via
    ``data()``, and translates exceptions into JSON responses with the
    appropriate status codes:

        - ValidationError: HTTP 409
        - Http404: HTTP 404
        - PermissionDenied: HTTP 403
        - ValueError: HTTP 400
    """
    def render_to_response(self, obj, **response_kwargs):
        return JsonResponse(obj, safe=False, **response_kwargs)

    def data(self):
        if self.request.method == 'GET':
            return self.request.GET
        return json.loads(self.request.body)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.auth(request, *args, **kwargs)
            return super(RestView, self).dispatch(request, *args, **kwargs)
        except ValidationError as e:
            return self.render_to_response(e.message_dict, status=409)
        except Http404 as e:
            return self.render_to_response(str(e), status=404)
        except PermissionDenied as e:
            return self.render_to_response(str(e), status=403)
        except ValueError as e:
            return self.render_to_response(str(e), status=400)


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
            if request.user.is_authenticated:
                raise
            else:
                return redirect_to_login(request.get_full_path())
        else:
            return super(AuthorizedMixin, self).dispatch(request, *args, **kwargs)
