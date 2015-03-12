# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import widgy.contrib.form_builder.models


class Migration(migrations.Migration):

    dependencies = [
        ('form_builder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='name',
            field=models.CharField(default=widgy.contrib.form_builder.models.untitled_form, help_text='A name to help identify this form. Only admins see this.', max_length=255, verbose_name='Name'),
            preserve_default=True,
        ),
    ]
