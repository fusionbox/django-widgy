# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import widgy.models.mixins
import widgy.contrib.form_builder.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('widgy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChoiceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('help_text', models.TextField(verbose_name='help text', blank=True)),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
                ('choices', models.TextField(help_text='Place each choice on a separate line.')),
                ('type', models.CharField(max_length=25, verbose_name='type', choices=[('select', 'Dropdown'), ('radios', 'Radio buttons')])),
            ],
            options={
                'abstract': False,
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EmailSuccessHandler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('include_form_data', models.BooleanField(default=True, help_text="Should the form's data be included in the email?", verbose_name='include form data')),
                ('to', models.EmailField(max_length=75, verbose_name='to')),
            ],
            options={
                'verbose_name': 'admin success email',
                'verbose_name_plural': 'admin success emails',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EmailUserHandler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('include_form_data', models.BooleanField(default=False, help_text="Should the form's data be included in the email?", verbose_name='include form data')),
                ('to_ident', models.CharField(max_length=36, verbose_name='to')),
            ],
            options={
                'verbose_name': 'user success email',
                'verbose_name_plural': 'user success emails',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FieldMappingValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('field_ident', models.CharField(max_length=36)),
            ],
            options={
                'verbose_name': 'mapped field',
                'verbose_name_plural': 'mapped field',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('help_text', models.TextField(verbose_name='help text', blank=True)),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='A name to help identify this form. Only admins see this.', max_length=255, verbose_name='Name')),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
            ],
            options={
                'verbose_name': 'form',
                'verbose_name_plural': 'forms',
            },
            bases=(widgy.models.mixins.TabbedContainer, widgy.models.mixins.StrDisplayNameMixin, widgy.models.mixins.StrictDefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FormBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'fields',
                'verbose_name_plural': 'fields',
            },
            bases=(widgy.models.mixins.DefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FormInput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('help_text', models.TextField(verbose_name='help text', blank=True)),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
                ('type', models.CharField(max_length=255, verbose_name='type', choices=[('text', 'Text'), ('number', 'Number'), ('email', 'Email'), ('tel', 'Telephone'), ('checkbox', 'Checkbox'), ('date', 'Date')])),
            ],
            options={
                'verbose_name': 'form input',
                'verbose_name_plural': 'form inputs',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FormMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'settings',
                'verbose_name_plural': 'settings',
            },
            bases=(widgy.models.mixins.StrictDefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form_ident', models.CharField(max_length=36)),
                ('form_node', models.ForeignKey(related_name='form_submissions', on_delete=django.db.models.deletion.PROTECT, to='widgy.Node')),
            ],
            options={
                'verbose_name': 'form submission',
                'verbose_name_plural': 'form submissions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.CharField(max_length=255)),
                ('field_ident', models.CharField(max_length=36)),
                ('value', models.TextField()),
                ('field_node', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='widgy.Node', null=True)),
                ('submission', models.ForeignKey(related_name='values', to='form_builder.FormSubmission')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('help_text', models.TextField(verbose_name='help text', blank=True)),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
                ('choices', models.TextField(help_text='Place each choice on a separate line.')),
                ('type', models.CharField(max_length=25, verbose_name='type', choices=[('checkboxes', 'Checkboxes'), ('select', 'Multi-select')])),
            ],
            options={
                'abstract': False,
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SaveDataHandler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'save data handler',
                'verbose_name_plural': 'save data handlers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmitButton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(default='submit', max_length=255, verbose_name='text')),
            ],
            options={
                'verbose_name': 'submit button',
                'verbose_name_plural': 'submit buttons',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SuccessHandlers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'success handlers',
                'verbose_name_plural': 'success handlers',
            },
            bases=(widgy.models.mixins.DefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SuccessMessageBucket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'success message',
                'verbose_name_plural': 'success messages',
            },
            bases=(widgy.models.mixins.DefaultChildrenMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Textarea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('help_text', models.TextField(verbose_name='help text', blank=True)),
                ('ident', django_extensions.db.fields.UUIDField(editable=False, blank=True)),
            ],
            options={
                'verbose_name': 'text area',
                'verbose_name_plural': 'text areas',
            },
            bases=(widgy.models.mixins.StrDisplayNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Uncaptcha',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'uncaptcha',
                'verbose_name_plural': 'uncaptchas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WebToLeadMapperHandler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oid', models.CharField(max_length=16, verbose_name='Organization ID (OID)')),
            ],
            options={
                'verbose_name': 'Salesforce Web-to-Lead',
                'verbose_name_plural': 'Salesforce Web-to-Lead',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageUpload',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('form_builder.fileupload',),
        ),
    ]
