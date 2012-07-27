import json
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from widgy.models import WidgetNode, ContentPage


def add_page(request):
    return HttpResponse('aafba')


def change_page(request, object_id):
    page = get_object_or_404(ContentPage, pk=object_id)

    return TemplateResponse(request, 'widgy/change_page.html', {
        'page': page,
        })



def more_json(obj):
    """
    Allows decimals and objects with `to_json` methods to be serialized.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError("%r is not JSON serializable" % (obj,))


class JsonResponseMixin(object):
    def render_to_response(self, obj, **response_kwargs):
        return HttpResponse(self.serialize(obj), content_type='application/json', **response_kwargs)

    def serialize(self, obj):
        try:
            obj = obj.to_json()
        except AttributeError:
            pass

        try:
            obj = [i.to_json() for i in obj]
        except (AttributeError, TypeError):
            pass

        return json.dumps(obj, default=more_json)

    def http_method_not_allowed(self, *args, **kwargs):
        resp = super(JsonResponseMixin, self).http_method_not_allowed(*args, **kwargs)
        resp['Content-Type'] = 'application/json'

        return resp


class JsonRequestMixin(object):
    def data(self):
        if self.request.method == 'GET':
            return self.request.GET
        else:
            assert self.request.META['CONTENT_TYPE'].startswith('application/json')
            return json.loads(self.request.body)


class RestView(JsonResponseMixin, JsonRequestMixin, View):
    def auth(*args, **kwargs):
        raise NotImplementedError("If you really want no authentication, override this method")

    def dispatch(self, *args, **kwargs):
        try:
            self.auth(*args, **kwargs)
            return super(RestView, self).dispatch(*args, **kwargs)
        except ValidationError as e:
            return self.render_to_response(e.message_dict, status=409)
        except Http404 as e:
            return self.render_to_response(None, status=404)
        except PermissionDenied as e:
            return self.render_to_response(str(e), status=403)
        except ValueError as e:
            return self.render_to_response(str(e), status=400)

    def options(self, request, *args, **kwargs):
        allow = []
        for method in self.http_method_names:
            if hasattr(self, method):
                allow.append(method.upper())
        r = self.render_to_response(None)
        r['Allow'] = ','.join(allow)
        return r



class WidgetView(RestView):
    def auth(*args, **kwargs):
        pass

    def get(self, request, node_pk):
        obj = WidgetNode.objects.get(pk=node_pk)
        return self.render_to_response(obj)

node = WidgetView.as_view()
