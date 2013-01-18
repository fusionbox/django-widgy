# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Markdown._edit_timestamp'
        db.add_column('page_builder_markdown', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'CalloutWidget._edit_timestamp'
        db.add_column('page_builder_calloutwidget', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Section._edit_timestamp'
        db.add_column('page_builder_section', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Accordion._edit_timestamp'
        db.add_column('page_builder_accordion', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'MainContent._edit_timestamp'
        db.add_column('page_builder_maincontent', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'DefaultLayout._edit_timestamp'
        db.add_column('page_builder_defaultlayout', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'CalloutBucket._edit_timestamp'
        db.add_column('page_builder_calloutbucket', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Sidebar._edit_timestamp'
        db.add_column('page_builder_sidebar', '_edit_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2013, 1, 17, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Markdown._edit_timestamp'
        db.delete_column('page_builder_markdown', '_edit_timestamp')

        # Deleting field 'CalloutWidget._edit_timestamp'
        db.delete_column('page_builder_calloutwidget', '_edit_timestamp')

        # Deleting field 'Section._edit_timestamp'
        db.delete_column('page_builder_section', '_edit_timestamp')

        # Deleting field 'Accordion._edit_timestamp'
        db.delete_column('page_builder_accordion', '_edit_timestamp')

        # Deleting field 'MainContent._edit_timestamp'
        db.delete_column('page_builder_maincontent', '_edit_timestamp')

        # Deleting field 'DefaultLayout._edit_timestamp'
        db.delete_column('page_builder_defaultlayout', '_edit_timestamp')

        # Deleting field 'CalloutBucket._edit_timestamp'
        db.delete_column('page_builder_calloutbucket', '_edit_timestamp')

        # Deleting field 'Sidebar._edit_timestamp'
        db.delete_column('page_builder_sidebar', '_edit_timestamp')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'page_builder.accordion': {
            'Meta': {'object_name': 'Accordion'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.callout': {
            'Meta': {'object_name': 'Callout'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'root_node': ('widgy.db.fields.WidgyField', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'page_builder.calloutbucket': {
            'Meta': {'object_name': 'CalloutBucket'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.calloutwidget': {
            'Meta': {'object_name': 'CalloutWidget'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'callout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page_builder.Callout']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.defaultlayout': {
            'Meta': {'object_name': 'DefaultLayout'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.maincontent': {
            'Meta': {'object_name': 'MainContent'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.markdown': {
            'Meta': {'object_name': 'Markdown'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rendered': ('django.db.models.fields.TextField', [], {})
        },
        'page_builder.section': {
            'Meta': {'object_name': 'Section'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1023'})
        },
        'page_builder.sidebar': {
            'Meta': {'object_name': 'Sidebar'},
            '_edit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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

    complete_apps = ['page_builder']