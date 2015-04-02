# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


def get_ancestors(orm, node):
    """
    copied from Treebeard
    """
    paths = [node.path[0:pos]
             for pos in range(0, len(node.path), 4)[1:]]
    return orm['widgy.Node'].objects.filter(path__in=paths).order_by('depth')


def get_children(orm, node):
    return orm['widgy.Node'].objects.filter(path__startswith=node.path).order_by('depth')


def get_content(orm, node):
    ct = orm['contenttypes.ContentType'].objects.get(pk=node.content_type_id)
    return orm['%s.%s' % (ct.app_label, ct.model)].objects.get(pk=node.content_id)


def get_node(orm, content):
    ct = orm['contenttypes.ContentType'].objects.get(app_label=content._meta.app_label, model=content._meta.model_name)
    return orm['widgy.Node'].objects.get(content_type_id=ct.pk, content_id=content.pk)


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        for h in orm['form_builder.EmailUserHandler'].objects.filter(to__isnull=False):
            try:
                h.to
            except ObjectDoesNotExist:
                pass
            else:
                h.to_ident = get_content(orm, h.to).ident
                h.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        for h in orm['form_builder.EmailUserHandler'].objects.exclude(to_ident=''):
            handler_node = get_node(orm, h)
            form_ct = orm['contenttypes.ContentType'].objects.get(app_label='form_builder', model='form')
            form_node = get_ancestors(orm, handler_node).get(content_type_id=form_ct.pk)
            forminput_ct = orm['contenttypes.ContentType'].objects.get(app_label='form_builder', model='forminput')
            for child in get_children(orm, form_node):
                if child.content_type_id == forminput_ct.pk:
                    forminput = get_content(orm, child)
                    if forminput.ident == h.to_ident:
                        h.to = child
            h.save()

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
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'form_builder.emailuserhandler': {
            'Meta': {'object_name': 'EmailUserHandler'},
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'null': 'True', 'to': "orm['widgy.Node']"}),
            'to_ident': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'form_builder.form': {
            'Meta': {'object_name': 'Form'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'Untitled form 8'", 'max_length': '255'})
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
    symmetrical = True
