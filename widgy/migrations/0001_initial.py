# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import widgy.db.fields
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnknownWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('content_id', models.PositiveIntegerField()),
                ('is_frozen', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VersionCommit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('publish_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='widgy.VersionCommit', null=True)),
                ('root_node', widgy.db.fields.WidgyField(to='widgy.Node', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VersionTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='widgy.VersionCommit', unique=True)),
                ('working_copy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='widgy.Node', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='versioncommit',
            name='tracker',
            field=models.ForeignKey(related_name='commits', to='widgy.VersionTracker'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together=set([('content_type', 'content_id')]),
        ),
    ]
