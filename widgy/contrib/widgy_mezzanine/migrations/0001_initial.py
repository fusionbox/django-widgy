# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import widgy.db.fields
import django.db.models.deletion
import widgy.contrib.widgy_mezzanine.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '__first__'),
        ('review_queue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WidgyPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('root_node', widgy.db.fields.VersionedWidgyField(on_delete=django.db.models.deletion.SET_NULL, verbose_name='widgy content', to='review_queue.ReviewedVersionTracker', null=True)),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'widgy page',
                'verbose_name_plural': 'widgy pages',
            },
            bases=(widgy.contrib.widgy_mezzanine.models.WidgyPageMixin, 'pages.page'),
        ),
        migrations.CreateModel(
            name='UndeletePage',
            fields=[
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'restore deleted page',
                'proxy': True,
            },
            bases=('widgy_mezzanine.widgypage',),
        ),
    ]
