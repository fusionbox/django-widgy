from haystack import indexes

from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.templatetags.widgy_tags import render_root
from widgy.utils import html_to_plaintext

class PageIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    date = indexes.DateTimeField(model_attr='publish_date')
    description = indexes.CharField(model_attr='description')
    keywords = indexes.MultiValueField()
    text = indexes.CharField(document=True)

    def get_model(self):
        return WidgyPage

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def prepare_text(self, obj):
        html = render_root({}, obj, 'root_node')
        content = html_to_plaintext(html)
        keywords = ' '.join(self.prepare_keywords(obj))
        return ' '.join([obj.title, keywords, obj.description,
                         content])

    def prepare_keywords(self, obj):
        return [unicode(k) for k in obj.keywords.all()]
