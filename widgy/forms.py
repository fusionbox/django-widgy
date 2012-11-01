from django import forms
from fusionbox.core.templatetags.fusionbox_tags import json


class WidgyFormWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        from widgy.models import Node
        node = Node.objects.get(pk=value)
        node_json = json(node.to_json())
        return u'''
<script data-main="/static/widgy/js/main" src="/static/widgy/js/require/require.js"></script>
  <div id="node_{value}" class="widgy"></div>
<script>
  require([ 'widgy' ], function(Widgy) {{
    window.widgy = new Widgy('#node_{value}', {json});
  }});
</script>
'''.format(value=value, json=node_json)


class WidgyFormField(forms.ModelChoiceField):
    widget = WidgyFormWidget
