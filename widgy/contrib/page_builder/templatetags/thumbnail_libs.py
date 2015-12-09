from django import template

from sorl.thumbnail.conf import settings
from sorl.thumbnail import default
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.parsers import parse_geometry

register = template.Library()


@register.tag
def sorl_thumbnail(*args, **kwargs):
    from sorl.thumbnail.templatetags.thumbnail import thumbnail
    return thumbnail(*args, **kwargs)


@register.tag
def easy_thumbnail(*args, **kwargs):
    from easy_thumbnails.templatetags.thumbnail import thumbnail
    return thumbnail(*args, **kwargs)


@register.filter
def sorl_margin(file_, geometry_string):
    """
    This is copied from sorl/thumbnail/templatetags/thumbnail.py because of
    problems with importing it.  This should be removed when we remove
    easy_thumbnail.

    Returns the calculated margin for an image and geometry
    """
    if not file_ or settings.THUMBNAIL_DUMMY:
        return 'auto'
    margin = [0, 0, 0, 0]
    image_file = default.kvstore.get_or_set(ImageFile(file_))
    x, y = parse_geometry(geometry_string, image_file.ratio)
    ex = x - image_file.x
    margin[3] = ex / 2
    margin[1] = ex / 2
    if ex % 2:
        margin[1] += 1
    ey = y - image_file.y
    margin[0] = ey / 2
    margin[2] = ey / 2
    if ey % 2:
        margin[2] += 1
    return ' '.join([ '%spx' % n for n in margin ])
