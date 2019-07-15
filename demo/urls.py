import django
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
import django.views.static

import mezzanine.core.views
import mezzanine.pages.views
from mezzanine.generic.views import admin_keywords_submit

from demo.widgysite import widgy_site

if django.VERSION < (1, 7):
    admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = [
    url('^admin/widgy/', include(widgy_site.urls)),
    url("^admin/", include(admin.site.urls)),
    url('^form/', include('widgy.contrib.widgy_mezzanine.urls')),

    # We don't want to presume how your homepage works, so here are a
    # few patterns you can use to set it up.

    # HOMEPAGE AS STATIC TEMPLATE
    # ---------------------------
    # This pattern simply loads the index.html template. It isn't
    # commented out like the others, so it's the default. You only need
    # one homepage pattern, so if you use a different one, comment this
    # one out.

    url(r'^$', mezzanine.pages.views.page, {'slug': '/'}, name='home'),

    # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
    # ---------------------------------------------
    # This pattern gives us a normal ``Page`` object, so that your
    # homepage can be managed via the page tree in the admin. If you
    # use this pattern, you'll need to create a page in the page tree,
    # and specify its URL (in the Meta Data section) as "/", which
    # is the value used below in the ``{"slug": "/"}`` part. Make
    # sure to uncheck "show in navigation" when you create the page,
    # since the link to the homepage is always hard-coded into all the
    # page menus that display navigation on the site. Also note that
    # the normal rule of adding a custom template per page with the
    # template name using the page's slug doesn't apply here, since
    # we can't have a template called "/.html" - so for this case, the
    # template "pages/index.html" can be used.

    # url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),

    # HOMEPAGE FOR A BLOG-ONLY SITE
    # -----------------------------
    # This pattern points the homepage to the blog post listing page,
    # and is useful for sites that are primarily blogs. If you use this
    # pattern, you'll also need to set BLOG_SLUG = "" in your
    # ``settings.py`` module, and delete the blog page object from the
    # page tree in the admin if it was installed.

    # url("^$", "mezzanine.blog.views.blog_post_list", name="home"),

    # MEZZANINE'S URLS
    # ----------------
    # Note: ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!
    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.
    url("^admin_keywords_submit/$", admin_keywords_submit, name="admin_keywords_submit"),
    url("^admin_page_ordering/$", mezzanine.pages.views.admin_page_ordering,
        name="admin_page_ordering"),
    url("^", include("mezzanine.urls")),

]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler500 = mezzanine.core.views.server_error

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
