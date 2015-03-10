# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import demo.demo_widgets.models
import widgy.models.mixins
import widgy.contrib.page_builder.db.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('page_builder', '0001_initial'),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
            ],
            options={
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, demo.demo_widgets.models.AcceptsSimpleHtmlChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Boxes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tagline', models.CharField(max_length=255, verbose_name='tagline')),
                ('background_image', widgy.contrib.page_builder.db.fields.ImageField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='background image', to='filer.File', null=True)),
            ],
            options={
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, demo.demo_widgets.models.AcceptsSimpleHtmlChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Slideshow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HomeLayout',
            fields=[
            ],
            options={
                'verbose_name': 'home layout',
                'proxy': True,
                'verbose_name_plural': 'home layouts',
            },
            bases=('page_builder.defaultlayout',),
        ),
    ]
