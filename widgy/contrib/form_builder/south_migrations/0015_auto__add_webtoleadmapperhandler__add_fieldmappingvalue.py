# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WebToLeadMapperHandler'
        db.create_table('form_builder_webtoleadmapperhandler', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('oid', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('form_builder', ['WebToLeadMapperHandler'])

        # Adding model 'FieldMappingValue'
        db.create_table('form_builder_fieldmappingvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_ident', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('form_builder', ['FieldMappingValue'])


    def backwards(self, orm):
        # Deleting model 'WebToLeadMapperHandler'
        db.delete_table('form_builder_webtoleadmapperhandler')

        # Deleting model 'FieldMappingValue'
        db.delete_table('form_builder_fieldmappingvalue')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'form_builder.choicefield': {
            'Meta': {'object_name': 'ChoiceField'},
            'choices': ('django.db.models.fields.TextField', [], {}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'form_builder.emailsuccesshandler': {
            'Meta': {'object_name': 'EmailSuccessHandler'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_form_data': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'form_builder.emailuserhandler': {
            'Meta': {'object_name': 'EmailUserHandler'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_form_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'form_builder.fieldmappingvalue': {
            'Meta': {'object_name': 'FieldMappingValue'},
            'field_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'form_builder.form': {
            'Meta': {'object_name': 'Form'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'Untitled form 1'", 'max_length': '255'})
        },
        'form_builder.formbody': {
            'Meta': {'object_name': 'FormBody'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.forminput': {
            'Meta': {'object_name': 'FormInput'},
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'form_builder.formmeta': {
            'Meta': {'object_name': 'FormMeta'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.formsubmission': {
            'Meta': {'object_name': 'FormSubmission'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'form_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'form_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'form_submissions'", 'on_delete': 'models.PROTECT', 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'form_builder.formvalue': {
            'Meta': {'object_name': 'FormValue'},
            'field_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'field_node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'values'", 'to': "orm['form_builder.FormSubmission']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'form_builder.multiplechoicefield': {
            'Meta': {'object_name': 'MultipleChoiceField'},
            'choices': ('django.db.models.fields.TextField', [], {}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'form_builder.savedatahandler': {
            'Meta': {'object_name': 'SaveDataHandler'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.submitbutton': {
            'Meta': {'object_name': 'SubmitButton'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "u'submit'", 'max_length': '255'})
        },
        'form_builder.successhandlers': {
            'Meta': {'object_name': 'SuccessHandlers'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.successmessagebucket': {
            'Meta': {'object_name': 'SuccessMessageBucket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.textarea': {
            'Meta': {'object_name': 'Textarea'},
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'form_builder.uncaptcha': {
            'Meta': {'object_name': 'Uncaptcha'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'form_builder.webtoleadmapperhandler': {
            'Meta': {'object_name': 'WebToLeadMapperHandler'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oid': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'widgy.node': {
            'Meta': {'unique_together': "[('content_type', 'content_id')]", 'object_name': 'Node'},
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