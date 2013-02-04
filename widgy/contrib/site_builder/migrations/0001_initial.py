# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WidgySite'
        db.create_table('site_builder_widgysite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(related_name='widgy_site', unique=True, on_delete=models.PROTECT, to=orm['sites.Site'])),
            ('root_node', self.gf('widgy.db.fields.WidgyField')(to=orm['widgy.Node'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('site_builder', ['WidgySite'])

        # Adding model 'SiteRoot'
        db.create_table('site_builder_siteroot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_nodes', self.gf('widgy.generic.ProxyGenericRelation')(object_id_field='content_id', to=orm['widgy.Node'])),
        ))
        db.send_create_signal('site_builder', ['SiteRoot'])

        # Adding model 'ContentPage'
        db.create_table('site_builder_contentpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('root_node', self.gf('widgy.db.fields.VersionedWidgyField')(to=orm['widgy.VersionTracker'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('_nodes', self.gf('widgy.generic.ProxyGenericRelation')(object_id_field='content_id', to=orm['widgy.Node'])),
        ))
        db.send_create_signal('site_builder', ['ContentPage'])

        # Adding model 'PageMeta'
        db.create_table('site_builder_pagemeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_sitemap', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_top_nav', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_footer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('seo_title', self.gf('django.db.models.fields.CharField')(max_length=75, blank=True)),
            ('seo_description', self.gf('django.db.models.fields.TextField')(max_length=150, blank=True)),
            ('seo_keywords', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
            ('_nodes', self.gf('widgy.generic.ProxyGenericRelation')(object_id_field='content_id', to=orm['widgy.Node'])),
        ))
        db.send_create_signal('site_builder', ['PageMeta'])

        # Adding model 'InternalRedirect'
        db.create_table('site_builder_internalredirect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_permanant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('_nodes', self.gf('widgy.generic.ProxyGenericRelation')(object_id_field='content_id', to=orm['widgy.Node'])),
        ))
        db.send_create_signal('site_builder', ['InternalRedirect'])

        # Adding model 'ExternalRedirect'
        db.create_table('site_builder_externalredirect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_permanant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('target', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('_nodes', self.gf('widgy.generic.ProxyGenericRelation')(object_id_field='content_id', to=orm['widgy.Node'])),
        ))
        db.send_create_signal('site_builder', ['ExternalRedirect'])


    def backwards(self, orm):
        # Deleting model 'WidgySite'
        db.delete_table('site_builder_widgysite')

        # Deleting model 'SiteRoot'
        db.delete_table('site_builder_siteroot')

        # Deleting model 'ContentPage'
        db.delete_table('site_builder_contentpage')

        # Deleting model 'PageMeta'
        db.delete_table('site_builder_pagemeta')

        # Deleting model 'InternalRedirect'
        db.delete_table('site_builder_internalredirect')

        # Deleting model 'ExternalRedirect'
        db.delete_table('site_builder_externalredirect')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'site_builder.contentpage': {
            'Meta': {'object_name': 'ContentPage'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root_node': ('widgy.db.fields.VersionedWidgyField', [], {'to': "orm['widgy.VersionTracker']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'site_builder.externalredirect': {
            'Meta': {'object_name': 'ExternalRedirect'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_permanant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'target': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'site_builder.internalredirect': {
            'Meta': {'object_name': 'InternalRedirect'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_permanant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'site_builder.pagemeta': {
            'Meta': {'object_name': 'PageMeta'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_footer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_sitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_top_nav': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'seo_description': ('django.db.models.fields.TextField', [], {'max_length': '150', 'blank': 'True'}),
            'seo_keywords': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'seo_title': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'site_builder.siteroot': {
            'Meta': {'object_name': 'SiteRoot'},
            '_nodes': ('widgy.generic.ProxyGenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['widgy.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'site_builder.widgysite': {
            'Meta': {'object_name': 'WidgySite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root_node': ('widgy.db.fields.WidgyField', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'widgy_site'", 'unique': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['sites.Site']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        },
        'widgy.versioncommit': {
            'Meta': {'object_name': 'VersionCommit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['widgy.VersionCommit']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'root_node': ('widgy.db.fields.WidgyField', [], {'to': "orm['widgy.Node']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['widgy.VersionTracker']"})
        },
        'widgy.versiontracker': {
            'Meta': {'object_name': 'VersionTracker'},
            'head': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['widgy.VersionCommit']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'working_copy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['widgy.Node']", 'on_delete': 'models.PROTECT'})
        }
    }

    complete_apps = ['site_builder']