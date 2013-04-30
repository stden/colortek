# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SMSLogger'
        db.create_table('sms_smslogger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mid', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 16, 23, 24, 40, 778210), auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 16, 23, 24, 40, 778269), auto_now=True, blank=True)),
            ('submited', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='2', max_length=10)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('provider', self.gf('django.db.models.fields.CharField')(default='smsdirect', max_length=15)),
        ))
        db.send_create_signal('sms', ['SMSLogger'])

        # Adding unique constraint on 'SMSLogger', fields ['mid', 'provider']
        db.create_unique('sms_smslogger', ['mid', 'provider'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SMSLogger', fields ['mid', 'provider']
        db.delete_unique('sms_smslogger', ['mid', 'provider'])

        # Deleting model 'SMSLogger'
        db.delete_table('sms_smslogger')


    models = {
        'sms.smslogger': {
            'Meta': {'unique_together': "(('mid', 'provider'),)", 'object_name': 'SMSLogger'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 16, 23, 24, 40, 778210)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mid': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "'smsdirect'", 'max_length': '15'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '10'}),
            'submited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 16, 23, 24, 40, 778269)', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms']
