# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page_builder', '0002_add_site_to_callout'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='style',
            field=models.CharField(blank=True, choices=[('alternating', 'Alternating'), ('bordered', 'Bordered')], max_length=50),
        ),
    ]
