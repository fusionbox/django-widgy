import warnings

from widgy.signals import widgy_pre_index


warnings.warn(
    "widgy.contrib.widgy_mezzanine.signals.widgypage_pre_index is deprecated. "
    "Use widgy.signals.widgy_pre_index instead.",
    DeprecationWarning,
)

widgypage_pre_index = widgy_pre_index
