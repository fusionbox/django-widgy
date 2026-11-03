from django import template

register = template.Library()


@register.tag
def easy_thumbnail(*args, **kwargs):
    """
    Alias for easy_thumbnails' ``thumbnail`` tag under a name that cannot
    collide with other thumbnailing libraries (notably sorl.thumbnail, which
    also ships a template tag library called ``thumbnail``). widgy's own
    templates load this library so they keep working in projects that install
    sorl alongside easy_thumbnails.
    """
    from easy_thumbnails.templatetags.thumbnail import thumbnail
    return thumbnail(*args, **kwargs)
