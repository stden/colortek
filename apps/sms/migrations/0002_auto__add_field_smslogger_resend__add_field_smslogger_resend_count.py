# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SMSLogger.resend'
        db.add_column('sms_smslogger', 'resend', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'SMSLogger.resend_count'
        db.add_column('sms_smslogger', 'resend_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SMSLogger.resend'
        db.delete_column('sms_smslogger', 'resend')

        # Deleting field 'SMSLogger.resend_count'
        db.delete_column('sms_smslogger', 'resend_count')


    models = {
        'sms.smslogger': {
            'Meta': {'unique_together': "(('mid', 'provider'),)", 'object_name': 'SMSLogger'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 18, 18, 4, 48, 184170)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mid': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "'smsdirect'", 'max_length': '15'}),
            'resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resend_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '10'}),
            'submited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 18, 18, 4, 48, 184240)', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms']
