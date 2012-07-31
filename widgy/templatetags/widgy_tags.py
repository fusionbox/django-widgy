from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def render(context, content):
    # AttributeError is consumed by the templating engine so we make it an
    # AssertionError
    assert hasattr(content, 'render')

    return content.render(context)
