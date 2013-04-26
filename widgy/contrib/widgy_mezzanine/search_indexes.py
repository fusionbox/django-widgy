from haystack import indexes

from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.templatetags.widgy_tags import render_root
from widgy.utils import html_to_plaintext

class PageIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField()
    date = indexes.DateTimeField(model_attr='publish_date')
    description = indexes.CharField()
    keywords = indexes.MultiValueField()
    text = indexes.CharField(document=True)

    def get_model(self):
        return WidgyPage

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def prepare_text(self, obj):
        html = render_root({}, obj, 'root_node')
        return html_to_plaintext(html)
