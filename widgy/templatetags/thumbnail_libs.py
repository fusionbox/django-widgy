from django import template

register = template.Library()


@register.tag
def sorl_thumbnail(*args, **kwargs):
    from sorl.thumbnail.templatetags.thumbnail import thumbnail
    return thumbnail(*args, **kwargs)


@register.tag
def easy_thumbnail(*args, **kwargs):
    from easy_thumbnails.templatetags.thumbnail import thumbnail
    return thumbnail(*args, **kwargs)
