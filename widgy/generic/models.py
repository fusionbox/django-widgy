from django.contrib.contenttypes.models import ContentType, ContentTypeManager

try:
    from django.utils.encoding import smart_text
except ImportError:
    smart_text = lambda x: x

"""
This model adds the for_concrete_model option that was added in Django 1.5 to
Django 1.4.
"""

class ContentTypeManager(ContentTypeManager):
    _cache = {}

    def _get_opts(self, model, for_concrete_model):
        if for_concrete_model:
            model = model._meta.concrete_model
        elif model._deferred:
            model = model._meta.proxy_for_model
        return model._meta

    def get_for_model(self, model, for_concrete_model=True):
        """
        Returns the ContentType object for a given model, creating the
        ContentType if necessary. Lookups are cached so that subsequent lookups
        for the same model don't hit the database.
        """
        opts = self._get_opts(model, for_concrete_model)
        try:
            ct = self._get_from_cache(opts)
        except KeyError:
            # Load or create the ContentType entry. The smart_text() is
            # needed around opts.verbose_name_raw because name_raw might be a
            # django.utils.functional.__proxy__ object.
            ct, created = self.get_or_create(
                app_label = opts.app_label,
                model = opts.object_name.lower(),
                defaults = {'name': smart_text(opts.verbose_name_raw)},
            )
            self._add_to_cache(self.db, ct)

        return ct

    def get_for_models(self, *models, **kwargs):
        """
        Given *models, returns a dictionary mapping {model: content_type}.
        """
        for_concrete_models = kwargs.pop('for_concrete_models', True)
        # Final results
        results = {}
        # models that aren't already in the cache
        needed_app_labels = set()
        needed_models = set()
        needed_opts = set()
        for model in models:
            opts = self._get_opts(model, for_concrete_models)
            try:
                ct = self._get_from_cache(opts)
            except KeyError:
                needed_app_labels.add(opts.app_label)
                needed_models.add(opts.object_name.lower())
                needed_opts.add(opts)
            else:
                results[model] = ct
        if needed_opts:
            cts = self.filter(
                app_label__in=needed_app_labels,
                model__in=needed_models
            )
            for ct in cts:
                model = ct.model_class()
                if model._meta in needed_opts:
                    results[model] = ct
                    needed_opts.remove(model._meta)
                self._add_to_cache(self.db, ct)
        for opts in needed_opts:
            # These weren't in the cache, or the DB, create them.
            ct = self.create(
                app_label=opts.app_label,
                model=opts.object_name.lower(),
                name=smart_text(opts.verbose_name_raw),
            )
            self._add_to_cache(self.db, ct)
            results[ct.model_class()] = ct
        return results


class ContentType(ContentType):
    objects = ContentTypeManager()

    class Meta:
        proxy = True
