from django.dispatch import Signal

tree_changed = Signal(providing_args=["node", "content"])
