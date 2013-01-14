from django.test import TestCase

from widgy.generic.models import ContentType

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

    def test_fake_contenttype(self):
        self.assertEqual(Proxy, ContentType.objects.get_for_model(Proxy, for_concrete_model=False).model_class())
        self.assertEqual(Proxy, ContentType.objects.get_for_models(Proxy, for_concrete_models=False).values()[0].model_class())
