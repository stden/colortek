# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Container.codename'
        db.delete_column('catalog_container', 'codename')


    def backwards(self, orm):
        
        # Adding field 'Container.codename'
        db.add_column('catalog_container', 'codename', self.gf('django.db.models.fields.CharField')(default='nothing', max_length=32, unique=True), keep_default=False)


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
            'container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_container_set'", 'null': 'True', 'to': "orm['catalog.Container']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        }
    }

    complete_apps = ['catalog']
