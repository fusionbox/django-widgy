from django import forms
from fusionbox.core.templatetags.fusionbox_tags import json


WIDGY_FIELD_TEMPLATE = u"""
<script data-main="/static/widgy/js/main" src="/static/widgy/js/require/require.js"></script>
<div id="{html_id}" class="widgy"></div>
<script>
  require([ 'widgy' ], function(Widgy) {{
    window.widgy = new Widgy('#{html_id}', {json});
  }});
</script>
"""


class WidgyFormWidget(forms.Select):

    def render(self, name, value, attrs=None):
        if value:
            from widgy.models import Node
            node = Node.objects.get(pk=value)
            node_json = json(node.to_json())
            return WIDGY_FIELD_TEMPLATE.format(
                html_id=attrs['id'],
                json=node_json,
            )
        else:
            return super(WidgyFormWidget, self).render(name, value, attrs)


class WidgyFormField(forms.ModelChoiceField):
    widget = WidgyFormWidget
