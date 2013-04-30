# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SMSLogger', fields ['mid', 'provider']
        db.delete_unique('sms_smslogger', ['mid', 'provider'])


    def backwards(self, orm):
        # Adding unique constraint on 'SMSLogger', fields ['mid', 'provider']
        db.create_unique('sms_smslogger', ['mid', 'provider'])


    models = {
        'sms.smslogger': {
            'Meta': {'object_name': 'SMSLogger'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mid': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "'disms'", 'max_length': '15'}),
            'resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resend_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '10'}),
            'submited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 25, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms']