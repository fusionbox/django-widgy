# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlconfIncludePage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('urlconf_name', models.CharField(max_length=255, verbose_name='plugin name', choices=settings.URLCONF_INCLUDE_CHOICES)),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'plugin',
                'verbose_name_plural': 'plugins',
            },
            bases=('pages.page',),
        ),
    ]
