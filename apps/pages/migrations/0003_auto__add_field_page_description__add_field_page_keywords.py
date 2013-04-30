# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.description'
        db.add_column('pages_page', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=4096, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Page.keywords'
        db.add_column('pages_page', 'keywords',
                      self.gf('django.db.models.fields.CharField')(max_length=4096, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Page.description'
        db.delete_column('pages_page', 'description')

        # Deleting field 'Page.keywords'
        db.delete_column('pages_page', 'keywords')


    models = {
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'pages.textblock': {
            'Meta': {'object_name': 'TextBlock'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pages']