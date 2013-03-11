# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = [
        ('widgy', '0001_initial'),
    ]

    def forwards(self, orm):
        # Adding model 'MainContent'
        db.create_table('page_builder_maincontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page_builder', ['MainContent'])

        # Adding model 'Sidebar'
        db.create_table('page_builder_sidebar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page_builder', ['Sidebar'])

        # Adding model 'DefaultLayout'
        db.create_table('page_builder_defaultlayout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page_builder', ['DefaultLayout'])

        # Adding model 'Markdown'
        db.create_table('page_builder_markdown', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('widgy.contrib.page_builder.db.fields.MarkdownField')(blank=True)),
            ('rendered', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('page_builder', ['Markdown'])

        # Adding model 'CalloutBucket'
        db.create_table('page_builder_calloutbucket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page_builder', ['CalloutBucket'])

        # Adding model 'Callout'
        db.create_table('page_builder_callout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('root_node', self.gf('widgy.db.fields.WidgyField')(to=orm['widgy.Node'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('page_builder', ['Callout'])

        # Adding model 'CalloutWidget'
        db.create_table('page_builder_calloutwidget', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('callout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page_builder.Callout'], null=True, blank=True)),
        ))
        db.send_create_signal('page_builder', ['CalloutWidget'])

        # Adding model 'Accordion'
        db.create_table('page_builder_accordion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page_builder', ['Accordion'])

        # Adding model 'Section'
        db.create_table('page_builder_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1023)),
        ))
        db.send_create_signal('page_builder', ['Section'])


    def backwards(self, orm):
        # Deleting model 'MainContent'
        db.delete_table('page_builder_maincontent')

        # Deleting model 'Sidebar'
        db.delete_table('page_builder_sidebar')

        # Deleting model 'DefaultLayout'
        db.delete_table('page_builder_defaultlayout')

        # Deleting model 'Markdown'
        db.delete_table('page_builder_markdown')

        # Deleting model 'CalloutBucket'
        db.delete_table('page_builder_calloutbucket')

        # Deleting model 'Callout'
        db.delete_table('page_builder_callout')

        # Deleting model 'CalloutWidget'
        db.delete_table('page_builder_calloutwidget')

        # Deleting model 'Accordion'
        db.delete_table('page_builder_accordion')

        # Deleting model 'Section'
        db.delete_table('page_builder_section')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.calloutwidget': {
            'Meta': {'object_name': 'CalloutWidget'},
            'callout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page_builder.Callout']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.defaultlayout': {
            'Meta': {'object_name': 'DefaultLayout'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.maincontent': {
            'Meta': {'object_name': 'MainContent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'page_builder.markdown': {
            'Meta': {'object_name': 'Markdown'},
            'content': ('widgy.contrib.page_builder.db.fields.MarkdownField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rendered': ('django.db.models.fields.TextField', [], {})
        },
        'page_builder.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1023'})
        },
        'page_builder.sidebar': {
            'Meta': {'object_name': 'Sidebar'},
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
