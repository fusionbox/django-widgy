from __future__ import absolute_import

from widgy.contrib.review_queue.site import ReviewedWidgySite


class DemoWidgySite(ReviewedWidgySite):
    def valid_parent_of(self, parent, child_class, obj=None):
        from widgy.contrib.widgy_i18n.models import I18NLayout
        if isinstance(parent, I18NLayout):
            return True
        else:
            return super(DemoWidgySite, self).valid_parent_of(parent, child_class, obj)

widgy_site = DemoWidgySite()

