# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table('pages_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 25, 0, 0), auto_now=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 25, 0, 0), auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pages', ['Page'])

        # Adding model 'TextBlock'
        db.create_table('pages_textblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 25, 0, 0), auto_now=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 25, 0, 0), auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pages', ['TextBlock'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table('pages_page')

        # Deleting model 'TextBlock'
        db.delete_table('pages_textblock')


    models = {
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'pages.textblock': {
            'Meta': {'object_name': 'TextBlock'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pages']