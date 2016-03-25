from __future__ import unicode_literals

import os
import re
import six

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from filer.fields.file import FilerFileField
from filer.models.filemodels import File

from widgy.contrib.page_builder.forms import MarkdownField as MarkdownFormField, MarkdownWidget

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:  # South not installed
    pass
else:
    add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.MarkdownField"])
    add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.VideoField"])
    add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.ImageField"])


class MarkdownField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': MarkdownFormField,
            'widget': MarkdownWidget,
        }

        defaults.update(kwargs)

        return super(MarkdownField, self).formfield(**defaults)


class VideoUrl(six.text_type):

    def __new__(cls, regex):
        self = super(VideoUrl, cls).__new__(cls, regex.string)
        self.regex = regex
        return self

    @property
    def video_id(self):
        return self.regex.group('id')

class YoutubeUrl(VideoUrl):
    @property
    def embed_url(self):
        return '//youtube.com/embed/{0}'.format(self.video_id)


class VimeoUrl(VideoUrl):
    @property
    def embed_url(self):
        return '//player.vimeo.com/video/{0}'.format(self.video_id)


class CNBCUrl(VideoUrl):
    @property
    def embed_url(self):
        return '//plus.cnbc.com/rssvideosearch/action/player/id/{0}/code/cnbcplayershare'.format(self.video_id)


VIDEO_URL_CLASSES = {
    r'^https?:\/\/(?:www\.)?youtube.com\/watch\?(?=.*v=(?P<id>[\w-]+))(?:\S+)?$': YoutubeUrl,
    r'^https?:\/\/youtu\.be\/(?P<id>[\w-]+)$': YoutubeUrl,
    r'^https?:\/\/(?:www\.)?vimeo.com\/(?P<id>\d+)$': VimeoUrl,
    r'^https?:\/\/video.cnbc.com/gallery/\?(?=.*video=(?P<id>\d+))(?:\S*)$': CNBCUrl,
}


def validators_video_url(value):
    """
    Inspired by https://gist.github.com/2830057
    """
    if not any(re.match(pattern, value) for pattern in VIDEO_URL_CLASSES.keys()):
        raise forms.ValidationError(_('Not a valid YouTube or Vimeo URL'))


class VideoField(six.with_metaclass(models.SubfieldBase, models.URLField)):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', _('Please enter a link to the YouTube or'
                                         ' Vimeo page for this video.  i.e.'
                                         ' http://www.youtube.com/watch?v=9bZkp7q19f0'))
        super(VideoField, self).__init__(*args, **kwargs)
        self.validators.append(validators_video_url)

    def from_db_value(self, value, expression, connection, context):
        """Convert from db starting in Django 1.8"""
        if value is None:
            return value
        return self.get_url_instance(value)

    def to_python(self, value):
        """Convert from db in Django < 1.8"""
        url = super(VideoField, self).to_python(value)
        if url is None:
            return url
        return self.get_url_instance(url)

    def get_url_instance(cls, value):
        for pattern in VIDEO_URL_CLASSES.keys():
            match = re.match(pattern, value)
            if match:
                UrlClass = VIDEO_URL_CLASSES[pattern]
                return UrlClass(match)
        return value


class ImageField(FilerFileField):
    """
    This is here for backwards compatibility, but shouldn't be used. Instead use
    filer.fields.image.FilerImageField.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'null': True,
            'related_name': '+',
            # What should happen on_delete.  Set to models.PROTECT so this is harder to
            # ignore and forget about.
            'on_delete': models.PROTECT,
        }
        defaults.update(kwargs)
        super(ImageField, self).__init__(*args, **defaults)

    def validate(self, value, model_instance):
        file_obj = File.objects.get(pk=value)
        iext = os.path.splitext(file_obj.file.name)[1].lower()
        if not iext in ['.jpg', '.jpeg', '.png', '.gif']:
            raise forms.ValidationError('File type must be jpg, png, or gif')
