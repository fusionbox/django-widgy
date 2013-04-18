class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize(request, self)


class AuthorizedMixin(WidgyViewMixin):
    def dispatch(self, *args, **kwargs):
        self.auth(*args, **kwargs)
        return super(AuthorizedMixin, self).dispatch(*args, **kwargs)
