# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, connection
import uuid


def convert_to_uuid(apps, schema_editor):
    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE "form_builder_emailuserhandler" ALTER COLUMN "to_ident" TYPE uuid USING to_ident::uuid;
            ALTER TABLE "form_builder_formsubmission" ALTER COLUMN "form_ident" TYPE uuid USING form_ident::uuid;
            ALTER TABLE "form_builder_formvalue" ALTER COLUMN "field_ident" TYPE uuid USING field_ident::uuid;
            ALTER TABLE "form_builder_fieldmappingvalue" ALTER COLUMN "field_ident" TYPE uuid USING field_ident::uuid;
            ALTER TABLE "form_builder_form" ALTER COLUMN "ident" TYPE uuid USING ident::uuid;
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ('form_builder', '0003_auto_20150730_1401'),
    ]

    operations = [
        migrations.RunPython(convert_to_uuid, lambda apps, schema_editor: None),
        migrations.AlterModelOptions(
            name='form',
            options={'verbose_name': 'form', 'verbose_name_plural': 'form submissions'},
        ),
        migrations.AlterField(
            model_name='choicefield',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='emailuserhandler',
            name='to_ident',
            field=models.UUIDField(null=True, verbose_name='to'),
        ),
        migrations.AlterField(
            model_name='fieldmappingvalue',
            name='field_ident',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='form',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='forminput',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='formsubmission',
            name='form_ident',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='formvalue',
            name='field_ident',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='multiplechoicefield',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='textarea',
            name='ident',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
