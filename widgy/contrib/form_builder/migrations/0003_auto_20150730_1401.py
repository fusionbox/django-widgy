# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form_builder', '0002_auto_20150311_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsuccesshandler',
            name='to',
            field=models.EmailField(max_length=254, verbose_name='to'),
        ),
    ]
