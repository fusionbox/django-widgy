from django.template import Library
from django.contrib.admin.templatetags.admin_list import (
    result_list as result_list_orig,
    admin_actions as admin_actions_orig,
)

register = Library()

@register.inclusion_tag('admin/review_queue/reviewedversioncommit/change_list_results.html')
def result_list(cl):
    ctx = result_list_orig(cl)
    # our template needs each result (a list of strings), along with the
    # actual commit object.
    ctx['cl_results'] = zip(ctx['cl'].result_list, ctx['results'])
    return ctx

# This avoid importing admin_list tag which could conflict with result_list
# This does exactly the same as django.contrib.admin.templatetags.admin_list.admin_actions
@register.inclusion_tag('admin/actions.html', takes_context=True)
def admin_actions(context):
    return admin_actions_orig(context)
