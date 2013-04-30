# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'City'
        db.create_table('geo_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('geo', ['City'])

        # Adding model 'Subway'
        db.create_table('geo_subway', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.City'])),
        ))
        db.send_create_signal('geo', ['Subway'])


    def backwards(self, orm):
        
        # Deleting model 'City'
        db.delete_table('geo_city')

        # Deleting model 'Subway'
        db.delete_table('geo_subway')


    models = {
        'geo.city': {
            'Meta': {'ordering': "['-priority', 'id']", 'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'geo.subway': {
            'Meta': {'ordering': "['title']", 'object_name': 'Subway'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['geo']
