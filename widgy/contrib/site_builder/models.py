from django.db import models
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, redirect
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.http import Http404
from django.core.exceptions import ValidationError

from widgy.models import Content
from widgy import registry
from widgy.exceptions import ChildWasRejected
from widgy.db.fields import WidgyField, VersionedWidgyField

from widgy.contrib.page_builder.models import Layout

from widgy.contrib.site_builder.forms import ResourceForm


class WidgySite(models.Model):
    # TODO: `widgy_site` is a bad name for this.
    site = models.OneToOneField(Site, on_delete=models.PROTECT, related_name='widgy_site')

    root_node = WidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        verbose_name=_('Site Root'),
        root_choices=(
            'site_builder.SiteRoot',
        ))

    def get_edit_url(self):
        return reverse('admin:{m.app_label}_{m.module_name}_change'.format(m=self._meta), args=(self.pk,))


class SiteTreeContent(Content):
    def find_by_path(self, path):
        bits = filter(bool, path.strip('/').split('/', 1))

        if bits:
            bit, remainder = bits[0], bits[1:]
            try:
                next = filter(lambda content: content.slug == bit, self.get_children())[0]
            except IndexError:
                raise self.DoesNotExist
            if remainder:
                return next.find_by_path(remainder[0])
            return next
        else:
            return self

    def validate_child_slug(self, slug, child=None):
        if not slug:  # Duplicate emptly slugs are ok.
            return
        children = filter(
            lambda c: c != child,
            self.get_children(),
        )
        if any(c.slug == slug for c in children):
            raise ValidationError('Duplicate title.  Please choose a different title')

    class Meta:
        abstract = True


class SiteRoot(SiteTreeContent):
    accepting_children = True
    deletable = False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Resource)

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return False

registry.register(SiteRoot)


class Resource(SiteTreeContent):
    accepting_children = True
    editable = True
    form = ResourceForm

    slug = models.CharField(
        max_length=255,
        help_text='Only "a-z, 0-9, -, _" allowed.  Spaces will be converted to dashes',
        validators=[
            RegexValidator(r'[-0-9a-z_]+', 'Only "a-z, A-Z, 0-9, -, _" allowed'),
        ],
    )

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Resource)

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        if obj is not None:
            try:
                parent.validate_child_slug(obj.slug, obj)
            except ValidationError:
                raise ChildWasRejected
        return isinstance(parent, (SiteRoot, Resource))

    def get_absolute_url(self):
        slugs = [c.slug for c in self.get_ancestors()[1:]] + [self.slug]
        return '/{0}/'.format('/'.join(slugs))

    def get_edit_url(self):
        return reverse('admin:{m.app_label}_{m.module_name}_change'.format(m=self._meta), args=(self.pk,))

    def render_to_response(self, request):
        raise NotImplementedError

    class Meta:
        abstract = True


class ContentPage(Resource):
    # TODO: Figure out slug population from `slugify(root_node.head.title)` or
    # something similar.
    root_node = VersionedWidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        to=getattr(settings, 'WIDGY_MEZZANINE_VERSIONTRACKER', None),
        verbose_name=_('page content'),
        root_choices=(
            'site_builder.PageMeta',
        ))

    def render_to_response(self, request):
        if self.root_node.head is None:
            raise Http404
        context = {
            'page': self,
        }
        return render_to_response(
            self.get_render_templates(context),
            context,
            RequestContext(request),
        )

registry.register(ContentPage)


class PageMeta(Content):
    """
    A PageMeta serves as the root object for all content pages, allowing any
    Layout as a child, and storing all of the page meta information.
    """
    editable = True
    accepting_children = True

    title = models.CharField(max_length=255)

    is_published = models.BooleanField('published', default=True, blank=True)

    # Navigation
    in_sitemap = models.BooleanField('in sitemap', default=True, blank=True)
    in_top_nav = models.BooleanField('in top navigation', default=True, blank=True)
    in_footer = models.BooleanField('in footer', default=False, blank=True)

    # SEO Fields
    seo_title = models.CharField(max_length=75, blank=True)
    seo_description = models.TextField(max_length=150, blank=True)
    seo_keywords = models.TextField(max_length=1000, blank=True)

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Layout) and (not self.get_children() or obj in self.get_children())

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        if obj is not None:
            # TODO: check for slug namespace conflicts.
            pass
        return isinstance(parent, ContentPage)

registry.register(PageMeta)


class Redirect(Resource):
    is_permanant = models.BooleanField(blank=True, default=False)

    def render_to_response(self, request):
        return redirect(self.target, permanent=self.is_permanant)

    class Meta:
        abstract = True


class InternalRedirect(Redirect):
    target = models.CharField(
        max_length=1000,
        validators=[
            RegexValidator(r'[-0-9a-zA-Z_\/]+', 'Only "a-z, A-Z, 0-9, -, _, /" allowed'),
        ],
    )

registry.register(InternalRedirect)


class ExternalRedirect(Redirect):
    target = models.URLField(max_length=1000)

registry.register(ExternalRedirect)
