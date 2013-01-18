# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SubmitButton._edit_timestamp'
        db.add_column('form_builder_submitbutton', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'EmailSuccessHandler._edit_timestamp'
        db.add_column('form_builder_emailsuccesshandler', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Textarea._edit_timestamp'
        db.add_column('form_builder_textarea', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'FormInput._edit_timestamp'
        db.add_column('form_builder_forminput', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Form._edit_timestamp'
        db.add_column('form_builder_form', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SubmitButton._edit_timestamp'
        db.delete_column('form_builder_submitbutton', '_edit_timestamp')

        # Deleting field 'EmailSuccessHandler._edit_timestamp'
        db.delete_column('form_builder_emailsuccesshandler', '_edit_timestamp')

        # Deleting field 'Textarea._edit_timestamp'
        db.delete_column('form_builder_textarea', '_edit_timestamp')

        # Deleting field 'FormInput._edit_timestamp'
        db.delete_column('form_builder_forminput', '_edit_timestamp')

        # Deleting field 'Form._edit_timestamp'
        db.delete_column('form_builder_form', '_edit_timestamp')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'form_builder.emailsuccesshandler': {
            'Meta': {'object_name': 'EmailSuccessHandler'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'form_builder.form': {
            'Meta': {'object_name': 'Form'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.forminput': {
            'Meta': {'object_name': 'FormInput'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'form_builder.submitbutton': {
            'Meta': {'object_name': 'SubmitButton'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "'submit'", 'max_length': '255'})
        },
        'form_builder.textarea': {
            'Meta': {'object_name': 'Textarea'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'widgy.node': {
            'Meta': {'object_name': 'Node'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['form_builder']