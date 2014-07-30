from __future__ import absolute_import

from widgy.contrib.review_queue.site import ReviewedWidgySite


class DemoWidgySite(ReviewedWidgySite):
    pass


widgy_site = DemoWidgySite()
