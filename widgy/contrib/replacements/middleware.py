from django.contrib.sites.models import Site
from django.template.defaultfilters import escape
from widgy.contrib.replacements.models import (
        surrounded_by_curlies,
        Replacement
        )


class TagReplacementMiddleware:
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
        replacements = Replacement.published\
                .filter(site=Site.objects.get_current())\
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
