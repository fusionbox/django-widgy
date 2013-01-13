from django.test import TestCase

from .models import Base, Related, Proxy


class TestPGFK(TestCase):
    def test_works_like_gfk(self):
        base = Base()
        base.obj = Related.objects.create()
        base.save()

        base = Base.objects.get(pk=base.pk)
        self.assertIsInstance(base.obj, Related)

    def test_works_with_proxy(self):
        base = Base()
        base.obj = Proxy.objects.create()
        base.save()

        base = Base.objects.get(pk=base.pk)
        self.assertIsInstance(base.obj, Proxy)
        self.assertTrue(base.obj.some_method())

    def test_generic_relation(self):
        base = Base()
        base.obj = Proxy.objects.create()
        base.save()

        base = Base.objects.get(pk=base.pk)
        rel = Proxy.objects.get(pk=base.obj.pk)
        self.assertTrue(base in rel.bases.all())
