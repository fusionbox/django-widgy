def get_widgypage_model():
    from django.conf import settings
    from django.apps import apps
    from django.core.exceptions import ImproperlyConfigured

    try:
        app_label, model_name = getattr(settings, 'WIDGY_MEZZANINE_PAGE_MODEL', 'widgy_mezzanine.WidgyPage').split('.')
    except ValueError:
        raise ImproperlyConfigured("WIDGY_MEZZANINE_PAGE_MODEL must be of the form 'app_label.model_name'")
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise ImproperlyConfigured("WIDGY_MEZZANINE_PAGE_MODEL refers to model '%s' that has not been installed" % settings.WIDGY_MEZZANINE_PAGE_MODEL)
    return model
