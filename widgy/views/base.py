class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize(request, self)


class AuthorizedMixin(WidgyViewMixin):
    def dispatch(self, *args, **kwargs):
        self.auth(*args, **kwargs)
        return super(AuthorizedMixin, self).dispatch(*args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        view_func = super(AuthorizedMixin, cls).as_view(**initkwargs)
        view_func.view_instance = cls(**initkwargs)
        return view_func
