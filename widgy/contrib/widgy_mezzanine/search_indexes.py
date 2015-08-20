from haystack import indexes
from django.utils.encoding import force_text

from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.templatetags.widgy_tags import render_root
from widgy.utils import html_to_plaintext

from widgy.signals import widgy_pre_index

WidgyPage = get_widgypage_model()


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    date = indexes.DateTimeField(model_attr='publish_date')
    description = indexes.CharField(model_attr='description')
    keywords = indexes.MultiValueField()
    get_absolute_url = indexes.CharField(model_attr='get_absolute_url')
    text = indexes.CharField(document=True)

    def full_prepare(self, *args, **kwargs):
        widgy_pre_index.send(sender=self)
        return super(PageIndex, self).full_prepare(*args, **kwargs)

    def get_model(self):
        return WidgyPage

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def prepare_text(self, obj):
        context = {'_current_page': obj.page_ptr, 'page': obj.page_ptr}
        html = render_root(context, obj, 'root_node')
        content = html_to_plaintext(html)
        keywords = ' '.join(self.prepare_keywords(obj))
        return ' '.join([obj.title, keywords, obj.description,
                         content])

    def prepare_keywords(self, obj):
        return [force_text(k) for k in obj.keywords.all()]
