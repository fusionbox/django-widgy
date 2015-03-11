# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('widgy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewedVersionCommit',
            fields=[
                ('versioncommit_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='widgy.VersionCommit')),
                ('approved_at', models.DateTimeField(default=None, null=True)),
                ('approved_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'unapproved commit',
                'verbose_name_plural': 'unapproved commits',
            },
            bases=('widgy.versioncommit',),
        ),
        migrations.CreateModel(
            name='ReviewedVersionTracker',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('widgy.versiontracker',),
        ),
    ]
