import warnings

# This module used to contain a backport of for_concrete_model, which is now in
# all supported versions of django. This import remains for backwards
# compatibility.
from django.contrib.contenttypes.models import ContentType, ContentTypeManager  # NOQA

warnings.warn(
    "widgy.generic.models is deprecated. Use django.contrib.contentypes.models instead.",
    DeprecationWarning,
    stacklevel=2,
)
