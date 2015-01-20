from django.db import models
from django.test import TestCase


from widgy.compat import check_if_field_name_exists_on_cls


class FieldExistsModel(models.Model):
    field_a = models.IntegerField()


class ChildFieldExistsModel(FieldExistsModel):
    field_b = models.IntegerField()


class TestLinkField(TestCase):
    def test_for_existing_field(self):
        assert check_if_field_name_exists_on_cls('field_a', FieldExistsModel)

    def test_for_non_existant_field(self):
        assert not check_if_field_name_exists_on_cls('does_not_exist', FieldExistsModel)

    def test_for_existing_field_on_child_model(self):
        assert check_if_field_name_exists_on_cls('field_a', ChildFieldExistsModel)
        assert check_if_field_name_exists_on_cls('field_b', ChildFieldExistsModel)

    def test_for_non_existant_field_on_child_model(self):
        assert not check_if_field_name_exists_on_cls('does_not_exist', ChildFieldExistsModel)
        assert not check_if_field_name_exists_on_cls('does_not_exist', ChildFieldExistsModel)
