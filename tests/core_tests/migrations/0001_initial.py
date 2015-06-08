# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import widgy.db.fields
import widgy.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('widgy', '0001_initial'),
        ('review_queue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnotherLinkableThing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'bucket',
            },
        ),
        migrations.CreateModel(
            name='Button',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CantGoAnywhereWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CssClassesWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ForeignKeyWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='HasAWidgy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('widgy', widgy.db.fields.WidgyField(blank=True, to='widgy.Node', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HasAWidgyNonNull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('widgy', widgy.db.fields.WidgyField(to='widgy.Node')),
            ],
        ),
        migrations.CreateModel(
            name='HasAWidgyOnlyAnotherLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('widgy', widgy.db.fields.WidgyField(blank=True, to='widgy.Node', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='LinkableThing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LinkableThing3',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'ZZZZZ should be last',
            },
        ),
        migrations.CreateModel(
            name='MyInvisibleBucket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            bases=(widgy.models.mixins.InvisibleMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RawTextWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Related',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewedVersionedPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version_tracker', widgy.db.fields.VersionedWidgyField(to='review_queue.ReviewedVersionTracker')),
            ],
        ),
        migrations.CreateModel(
            name='ThingWithLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('linkable_object_id', models.PositiveIntegerField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='VariegatedFieldsWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('required_name', models.CharField(max_length=255)),
                ('optional_name', models.CharField(max_length=255, blank=True)),
                ('color', models.CharField(max_length=255, choices=[('r', 'Red'), ('g', 'Green'), ('b', 'Blue')])),
                ('date', models.DateField(null=True)),
                ('time', models.TimeField(null=True)),
                ('datetime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VerboseNameLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version_tracker', widgy.db.fields.VersionedWidgyField(blank=True, to='widgy.VersionTracker', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPage2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bar', widgy.db.fields.VersionedWidgyField(related_name='asdf', to='widgy.VersionTracker', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPage3',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('foo', widgy.db.fields.VersionedWidgyField(related_name='+', to='widgy.VersionTracker')),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPage4',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='VersionPageThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', models.ForeignKey(to='core_tests.VersionedPage4')),
                ('widgy', widgy.db.fields.VersionedWidgyField(related_name='+', to='widgy.VersionTracker')),
            ],
        ),
        migrations.CreateModel(
            name='WeirdPkBase',
            fields=[
                ('bubble', models.AutoField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='WidgetWithHTMLHelpText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Your<br>Name', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AnotherLayout',
            fields=[
                ('layout_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.Layout')),
            ],
            options={
                'verbose_name': '\xc0\xf1\xf6th\xe9r L\xe0y\xf6\xf9t',
                'verbose_name_plural': '\xc0\xf1\xf6th\xe9r L\xe0y\xf6\xf9ts',
            },
            bases=('core_tests.layout',),
        ),
        migrations.CreateModel(
            name='ChildThingWithLink',
            fields=[
                ('thingwithlink_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.ThingWithLink')),
            ],
            bases=('core_tests.thingwithlink',),
        ),
        migrations.CreateModel(
            name='CssClassesWidgetProperty',
            fields=[
                ('cssclasseswidget_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.CssClassesWidget')),
            ],
            bases=('core_tests.cssclasseswidget',),
        ),
        migrations.CreateModel(
            name='ImmovableBucket',
            fields=[
                ('bucket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.Bucket')),
            ],
            bases=('core_tests.bucket',),
        ),
        migrations.CreateModel(
            name='PickyBucket',
            fields=[
                ('bucket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.Bucket')),
            ],
            bases=('core_tests.bucket',),
        ),
        migrations.CreateModel(
            name='UnnestableWidget',
            fields=[
                ('bucket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.Bucket')),
            ],
            bases=('core_tests.bucket',),
        ),
        migrations.CreateModel(
            name='UnregisteredLayout',
            fields=[
                ('layout_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.Layout')),
            ],
            bases=('core_tests.layout',),
        ),
        migrations.CreateModel(
            name='VerboseNameLayoutChild',
            fields=[
                ('verbosenamelayout_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.VerboseNameLayout')),
            ],
            options={
                'verbose_name': 'Foobar',
            },
            bases=('core_tests.verbosenamelayout',),
        ),
        migrations.CreateModel(
            name='WeirdPkBucketBase',
            fields=[
                ('weirdpkbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.WeirdPkBase')),
            ],
            bases=('core_tests.weirdpkbase',),
        ),
        migrations.AddField(
            model_name='versionedpage4',
            name='widgies',
            field=models.ManyToManyField(to='widgy.VersionTracker', through='core_tests.VersionPageThrough'),
        ),
        migrations.AddField(
            model_name='thingwithlink',
            name='linkable_content_type',
            field=models.ForeignKey(related_name='+', editable=False, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='foreignkeywidget',
            name='foo',
            field=models.ForeignKey(to='core_tests.Related'),
        ),
        migrations.CreateModel(
            name='CssClassesWidgetSubclass',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core_tests.cssclasseswidget',),
        ),
        migrations.CreateModel(
            name='UndeletableRawTextWidget',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core_tests.rawtextwidget',),
        ),
        migrations.CreateModel(
            name='VowelBucket',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core_tests.bucket',),
        ),
        migrations.CreateModel(
            name='WeirdPkBucket',
            fields=[
                ('weirdpkbucketbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core_tests.WeirdPkBucketBase')),
            ],
            bases=('core_tests.weirdpkbucketbase',),
        ),
    ]
