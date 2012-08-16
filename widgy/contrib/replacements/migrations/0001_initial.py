# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Replacement'
        db.create_table('replacements_replacement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('publish_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='replacements', to=orm['sites.Site'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('replacement', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('replacements', ['Replacement'])


    def backwards(self, orm):
        # Deleting model 'Replacement'
        db.delete_table('replacements_replacement')


    models = {
        'replacements.replacement': {
            'Meta': {'ordering': "('tag',)", 'object_name': 'Replacement'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'publish_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'replacement': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replacements'", 'to': "orm['sites.Site']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['replacements']