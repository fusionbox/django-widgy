class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize(request)
