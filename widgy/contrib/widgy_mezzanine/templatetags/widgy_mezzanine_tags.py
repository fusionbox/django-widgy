from django.template import Library
from django.contrib.admin.templatetags.admin_list import (
    result_list as result_list_orig,
    admin_actions as admin_actions_orig,
)

register = Library()

@register.inclusion_tag('admin/widgy/versioncommit/change_list_results.html')
def result_list(cl):
    return result_list_orig(cl)

# This avoid importing admin_list tag which could conflict with result_list
# This does exactly the same as django.contrib.admin.templatetags.admin_list.admin_actions
@register.inclusion_tag('admin/actions.html', takes_context=True)
def admin_actions(context):
    return admin_actions_orig(context)
