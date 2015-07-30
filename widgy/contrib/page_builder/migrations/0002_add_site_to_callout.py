# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('page_builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='callout',
            name='site',
            field=models.ForeignKey(blank=True, to='sites.Site', null=True),
        ),
    ]
