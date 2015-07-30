# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import widgy.db.fields
import widgy.contrib.page_builder.db.fields
import django.db.models.deletion
import widgy.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('widgy', '0001_initial'),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accordion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'accordion',
                'verbose_name_plural': 'accordions',
            },
            bases=(widgy.models.mixins.DefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Button',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, null=True, verbose_name='text', blank=True)),
                ('link_object_id', models.PositiveIntegerField(null=True, editable=False)),
                ('link_content_type', models.ForeignKey(related_name='+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'button',
                'verbose_name_plural': 'buttons',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Callout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('root_node', widgy.db.fields.WidgyField(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Widgy Content', to='widgy.Node', null=True)),
            ],
            options={
                'verbose_name': 'callout',
                'verbose_name_plural': 'callouts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalloutBucket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'callout bucket',
                'verbose_name_plural': 'callout buckets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalloutWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('callout', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='page_builder.Callout', null=True)),
            ],
            options={
                'verbose_name': 'callout widget',
                'verbose_name_plural': 'callout widgets',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DefaultLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'default layout',
                'verbose_name_plural': 'default layouts',
            },
            bases=(widgy.models.mixins.StrictDefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Figure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.CharField(default='center', max_length=50, verbose_name='position', choices=[('left', 'Float left'), ('right', 'Float right'), ('center', 'Center')])),
                ('title', models.CharField(max_length=1023, null=True, verbose_name='title', blank=True)),
                ('caption', models.TextField(null=True, verbose_name='caption', blank=True)),
            ],
            options={
                'verbose_name': 'figure',
                'verbose_name_plural': 'figures',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GoogleMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=500, verbose_name='address')),
                ('type', models.CharField(default='roadmap', max_length=20, verbose_name='type', choices=[('roadmap', 'Road map'), ('satellite', 'Satellite'), ('hybrid', 'Hybrid'), ('terrain', 'Terrain')])),
            ],
            options={
                'verbose_name': 'Google map',
                'verbose_name_plural': 'Google maps',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Html',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'HTML',
                'verbose_name_plural': 'HTML editors',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', widgy.contrib.page_builder.db.fields.ImageField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='image', to='filer.File', null=True)),
            ],
            options={
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MainContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'main content',
                'verbose_name_plural': 'main contents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Markdown',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', widgy.contrib.page_builder.db.fields.MarkdownField(verbose_name='content', blank=True)),
                ('rendered', models.TextField(editable=False)),
            ],
            options={
                'verbose_name': 'markdown',
                'verbose_name_plural': 'markdowns',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Use a unique title for each section.', max_length=1023, verbose_name='title')),
            ],
            options={
                'verbose_name': 'section',
                'verbose_name_plural': 'sections',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Sidebar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'sidebar',
                'verbose_name_plural': 'sidebars',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'table',
                'verbose_name_plural': 'tables',
            },
            bases=(widgy.models.mixins.StrictDefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TableBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'table body',
                'verbose_name_plural': 'table bodies',
            },
            bases=(widgy.models.mixins.InvisibleMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TableData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'cell',
                'verbose_name_plural': 'cells',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TableHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'table header',
                'verbose_name_plural': 'table headers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TableHeaderData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'column',
                'verbose_name_plural': 'columns',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TableRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'row',
                'verbose_name_plural': 'rows',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnsafeHtml',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'unsafe HTML',
                'verbose_name_plural': 'unsafe HTML editors',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video', widgy.contrib.page_builder.db.fields.VideoField(help_text='Please enter a link to the YouTube or Vimeo page for this video.  i.e. http://www.youtube.com/watch?v=9bZkp7q19f0', verbose_name='video')),
            ],
            options={
                'verbose_name': 'video',
                'verbose_name_plural': 'videos',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Tabs',
            fields=[
            ],
            options={
                'verbose_name': 'tabs',
                'proxy': True,
                'verbose_name_plural': 'tabs',
            },
            bases=(widgy.models.mixins.TabbedContainer, 'page_builder.accordion'),
        ),
    ]
