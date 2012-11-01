from datetime import datetime
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.template.defaultfilters import escape
from widgy.contrib.replacements.models import (
        surrounded_by_curlies,
        Replacement
        )
### TODO: Move this to a utility function:
if getattr(settings, 'USE_TZ', False):
    from django.utils.timezone import utc

    now = datetime.utcnow().replace(tzinfo=utc)
else:
    now = datetime.now()


class TagReplacementMiddleware(object):
    """
    Handles replacement of {{ tags }} that have been set up as sitewide
    replacements.
    """
    def process_response(self, request, response):
        """
        After fetching all the replacements for this site, a regex substitution
        is run on the rendered_content of the response.  This replaces any
        matched tags with those defined in the database.
        """
        try:
            app_name = resolve(request.path).app_name
        except Resolver404:
            return response
        if app_name in settings.REPLACEMENTS_APP_BLACKLIST:
            return response

        replacements = Replacement.objects\
                .filter(is_published=True, publish_at__lte=now)\
                .all()
        repl_list = [(r.tag, escape(r.replacement)) for r in replacements]

        def repl_tags(match_obj):
            try:
                matched_tuple = filter(
                        lambda x: x[0] in match_obj.group(0),
                        repl_list)[0]
                # The replacement text is at index 1, (tag, replacement)
                return matched_tuple[1]
            except IndexError:
                # Doesn't raise. Unmatched tags should look stupid, not break
                # the page.
                return match_obj.group(0)
        response.content = surrounded_by_curlies.sub(
                repl_tags,
                response.content)
        return response
