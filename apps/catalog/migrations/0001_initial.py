# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Service'
        db.create_table('catalog_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('catalog', ['Service'])

        # Adding model 'Addon'
        db.create_table('catalog_addon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=100, max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('catalog', ['Addon'])

        # Adding model 'AddonList'
        db.create_table('catalog_addonlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('addon', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['catalog.Addon'])),
        ))
        db.send_create_signal('catalog', ['AddonList'])

        # Adding model 'Container'
        db.create_table('catalog_container', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ct_set_for_container', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['catalog.Service'])),
            ('addons', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.AddonList'], null=True, blank=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('catalog', ['Container'])

        # Adding model 'Item'
        db.create_table('catalog_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['catalog.Container'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=100, max_digits=10, decimal_places=2)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('is_special', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('catalog', ['Item'])


    def backwards(self, orm):
        
        # Deleting model 'Service'
        db.delete_table('catalog_service')

        # Deleting model 'Addon'
        db.delete_table('catalog_addon')

        # Deleting model 'AddonList'
        db.delete_table('catalog_addonlist')

        # Deleting model 'Container'
        db.delete_table('catalog_container')

        # Deleting model 'Item'
        db.delete_table('catalog_item')


    models = {
        'catalog.addon': {
            'Meta': {'object_name': 'Addon'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.addonlist': {
            'Meta': {'object_name': 'AddonList'},
            'addon': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['catalog.Addon']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.container': {
            'Meta': {'object_name': 'Container'},
            'addons': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.AddonList']", 'null': 'True', 'blank': 'True'}),
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ct_set_for_container'", 'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['catalog.Service']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.item': {
            'Meta': {'object_name': 'Item'},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['catalog.Container']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_special': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.service': {
            'Meta': {'object_name': 'Service'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalog']
