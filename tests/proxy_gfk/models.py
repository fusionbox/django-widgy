from django.db import models
from django.contrib.contenttypes.models import ContentType

from widgy.generic import ProxyGenericForeignKey, ProxyGenericRelation
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation


class Base(models.Model):
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    obj = ProxyGenericForeignKey('content_type', 'content_id')


class Related(models.Model):
    bases = ProxyGenericRelation(Base,
                content_type_field='content_type',
                object_id_field='content_id')

    content = models.CharField(max_length=255)


class AbstractModel(models.Model):
    bases = ProxyGenericRelation(Base,
                content_type_field='content_type',
                object_id_field='content_id')
    class Meta:
        abstract = True

class ConcreteModel(AbstractModel):
    pass

class Proxy(Related):
    def some_method(self):
        return True

    class Meta:
        proxy = True
