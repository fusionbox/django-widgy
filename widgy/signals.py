from django.dispatch import Signal


pre_delete_widget = Signal(providing_args=['instance', 'raw'])

tree_changed = Signal(providing_args=["node", "content"])
