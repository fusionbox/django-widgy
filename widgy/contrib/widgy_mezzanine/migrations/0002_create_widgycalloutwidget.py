# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import widgy.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('page_builder', '0002_add_site_to_callout'),
        ('widgy_mezzanine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MezzanineCalloutWidget',
            fields=[
            ],
            options={
                'verbose_name': 'callout widget',
                'verbose_name_plural': 'callout widgets',
                'proxy': True,
            },
            bases=('page_builder.calloutwidget',),
        ),
    ]
