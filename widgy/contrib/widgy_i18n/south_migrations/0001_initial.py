# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'I18NLayout'
        db.create_table(u'widgy_i18n_i18nlayout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal(u'widgy_i18n', ['I18NLayout'])

        # Adding model 'I18NLayoutContainer'
        db.create_table(u'widgy_i18n_i18nlayoutcontainer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'widgy_i18n', ['I18NLayoutContainer'])


    def backwards(self, orm):
        # Deleting model 'I18NLayout'
        db.delete_table(u'widgy_i18n_i18nlayout')

        # Deleting model 'I18NLayoutContainer'
        db.delete_table(u'widgy_i18n_i18nlayoutcontainer')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'widgy.node': {
            'Meta': {'object_name': 'Node'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_frozen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'widgy_i18n.i18nlayout': {
            'Meta': {'object_name': 'I18NLayout'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'widgy_i18n.i18nlayoutcontainer': {
            'Meta': {'object_name': 'I18NLayoutContainer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['widgy_i18n']