# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'SiteListCalloutContent'
        db.delete_table('demo_widgets_sitelistcalloutcontent')

        # Adding model 'I18NThing'
        db.create_table('demo_widgets_i18nthing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('widgy.db.fields.WidgyField')(to=orm['widgy.Node'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('demo_widgets', ['I18NThing'])


    def backwards(self, orm):
        # Adding model 'SiteListCalloutContent'
        db.create_table('demo_widgets_sitelistcalloutcontent', (
            ('header', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('demo_widgets', ['SiteListCalloutContent'])

        # Deleting model 'I18NThing'
        db.delete_table('demo_widgets_i18nthing')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'demo_widgets.i18nthing': {
            'Meta': {'object_name': 'I18NThing'},
            'description': ('widgy.db.fields.WidgyField', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'demo_widgets.twocontentlayout': {
            'Meta': {'object_name': 'TwoContentLayout'},
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

    complete_apps = ['demo_widgets']