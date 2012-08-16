import re
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from fusionbox.behaviors import Timestampable, Publishable
from django.db.models import CharField, ForeignKey

surrounded_by_curlies = re.compile(r'{{\s*[^\{\}]+\s*}}')

no_curlies_regex = re.compile(r'^[^\{\}]*$')

no_curlies_validator = RegexValidator(no_curlies_regex,
        message='The replacement tag may not contain "}" or "{"')


class Replacement(Timestampable, Publishable):
    """
    Replacement models represent a sitewide text replacement.  During every
    response, the body is checked for {{ tag }} and replaces with the
    corresponding replacement text.

    Requires installation of the `TagReplacementMiddleware`
    """
    site = ForeignKey(Site, related_name='replacements')
    tag = CharField(max_length=255,
            validators=[no_curlies_validator],
            help_text=u'When this text is encountered \
            anywhere on site surrounded by {{ }}, it will be replaced with \
            the replacement text.')
    replacement = CharField(max_length=255,
            help_text=u'This text replaces the tag.')

    class Meta:
        verbose_name = 'replacement'
        verbose_name_plural = 'replacements'
        ordering = ('tag',)
