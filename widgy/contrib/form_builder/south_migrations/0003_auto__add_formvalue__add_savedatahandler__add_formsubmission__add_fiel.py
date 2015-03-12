# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FormValue'
        db.create_table('form_builder_formvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['form_builder.FormSubmission'])),
            ('field_node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['widgy.Node'], null=True, on_delete=models.SET_NULL)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('field_ident', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('form_builder', ['FormValue'])

        # Adding model 'SaveDataHandler'
        db.create_table('form_builder_savedatahandler', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('form_builder', ['SaveDataHandler'])

        # Adding model 'FormSubmission'
        db.create_table('form_builder_formsubmission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 6, 0, 0))),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('form_node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='form_submissions', on_delete=models.PROTECT, to=orm['widgy.Node'])),
            ('form_ident', self.gf('django.db.models.fields.CharField')(max_length=36)),
        ))
        db.send_create_signal('form_builder', ['FormSubmission'])

        # Adding field 'Textarea.ident'
        db.add_column('form_builder_textarea', 'ident',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=36, blank=True),
                      keep_default=False)

        # Adding field 'FormInput.ident'
        db.add_column('form_builder_forminput', 'ident',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=36, blank=True),
                      keep_default=False)

        # Adding field 'Form.name'
        db.add_column('form_builder_form', 'name',
                      self.gf('django.db.models.fields.CharField')(default='Untitled form 4', max_length=255),
                      keep_default=False)

        # Adding field 'Form.ident'
        db.add_column('form_builder_form', 'ident',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=36, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'FormValue'
        db.delete_table('form_builder_formvalue')

        # Deleting model 'SaveDataHandler'
        db.delete_table('form_builder_savedatahandler')

        # Deleting model 'FormSubmission'
        db.delete_table('form_builder_formsubmission')

        # Deleting field 'Textarea.ident'
        db.delete_column('form_builder_textarea', 'ident')

        # Deleting field 'FormInput.ident'
        db.delete_column('form_builder_forminput', 'ident')

        # Deleting field 'Form.name'
        db.delete_column('form_builder_form', 'name')

        # Deleting field 'Form.ident'
        db.delete_column('form_builder_form', 'ident')


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
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'form_builder.form': {
            'Meta': {'object_name': 'Form'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Untitled form 4'", 'max_length': '255'})
        },
        'form_builder.forminput': {
            'Meta': {'object_name': 'FormInput'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'form_builder.formsubmission': {
            'Meta': {'object_name': 'FormSubmission'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 6, 0, 0)'}),
            'form_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'form_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form_submissions'", 'on_delete': 'models.PROTECT', 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'form_builder.formvalue': {
            'Meta': {'object_name': 'FormValue'},
            'field_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'field_node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['form_builder.FormSubmission']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'form_builder.savedatahandler': {
            'Meta': {'object_name': 'SaveDataHandler'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.submitbutton': {
            'Meta': {'object_name': 'SubmitButton'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "'submit'", 'max_length': '255'})
        },
        'form_builder.textarea': {
            'Meta': {'object_name': 'Textarea'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'widgy.node': {
            'Meta': {'object_name': 'Node'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_frozen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['form_builder']
