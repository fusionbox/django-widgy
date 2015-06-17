from django.dispatch import Signal


pre_delete_widget = Signal(providing_args=['instance', 'raw'])
widgy_pre_index = Signal()
