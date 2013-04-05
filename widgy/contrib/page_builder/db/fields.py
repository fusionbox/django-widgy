from __future__ import unicode_literals

import urlparse
import re

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from widgy.contrib.page_builder.forms import MarkdownField as MarkdownFormField, MarkdownWidget

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.MarkdownField"])
add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.VideoField"])


class MarkdownField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': MarkdownFormField,
            'widget': MarkdownWidget,
        }

        defaults.update(kwargs)

        return super(MarkdownField, self).formfield(**defaults)


class VideoUrl(unicode):
    @property
    def video_id(self):
        parsed_url = urlparse.urlparse(self)
        if parsed_url.query == '':
            return parsed_url.path[1:]
        return urlparse.parse_qs(parsed_url.query)['v'][0]


class YoutubeUrl(VideoUrl):
    @property
    def embed_url(self):
        return '//youtube.com/embed/{0}'.format(self.video_id)


class VimeoUrl(VideoUrl):
    @property
    def embed_url(self):
        return '//player.vimeo.com/video/{0}'.format(self.video_id)


VIDEO_URL_CLASSES = {
    r'^https?:\/\/(?:www\.)?youtube.com\/watch\?(?=.*v=\w+)(?:\S+)?$': YoutubeUrl,
    r'^https?:\/\/youtu\.be\/(\w+)$': YoutubeUrl,
    r'^https?:\/\/(?:www\.)?vimeo.com\/(\d+)$': VimeoUrl,
}


def validators_video_url(value):
    """
    Inspired by https://gist.github.com/2830057
    """
    if not any(re.match(pattern, value) for pattern in VIDEO_URL_CLASSES.keys()):
        raise forms.ValidationError(_('Not a valid YouTube or Vimeo URL'))


class VideoField(models.URLField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', _('Please enter a link to the YouTube or'
                                         ' Vimeo page for this video.  i.e.'
                                         ' http://www.youtube.com/watch?v=9bZkp7q19f0'))
        super(VideoField, self).__init__(*args, **kwargs)
        self.validators.append(validators_video_url)

    def to_python(self, value):
        url = super(VideoField, self).to_python(value)
        return self.get_url_instance(url)

    def get_url_instance(cls, value):
        for pattern in VIDEO_URL_CLASSES.keys():
            if re.match(pattern, value):
                UrlClass = VIDEO_URL_CLASSES[pattern]
                return UrlClass(value)
        return value
