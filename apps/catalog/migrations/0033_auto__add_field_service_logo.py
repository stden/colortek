# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Service.logo'
        db.add_column('catalog_service', 'logo',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Service.logo'
        db.delete_column('catalog_service', 'logo')


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
            'address': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'avarage_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'avarage_deliver_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'avarage_deliver_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'bonus_score': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'building': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['geo.City']"}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'glat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'glng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invites': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_operator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_partner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Service']", 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '265', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'subway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Subway']", 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'catalog.addon': {
            'Meta': {'object_name': 'Addon'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'addon_list_set'", 'to': "orm['catalog.AddonList']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.addonlist': {
            'Meta': {'object_name': 'AddonList'},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'addon_list_container_set'", 'to': "orm['catalog.Container']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.atommeanrating': {
            'Meta': {'object_name': 'AtomMeanRating'},
            'atom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'atom_mean_rating_voteatom_set'", 'to': "orm['catalog.VoteAtom']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'atom_mean_rating_user_set'", 'to': "orm['auth.User']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'atom_mean_rating_service_set'", 'to': "orm['catalog.Service']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        'catalog.bonustransaction': {
            'Meta': {'object_name': 'BonusTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bonus_client_set'", 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'exchange_rate': ('django.db.models.fields.DecimalField', [], {'default': "'0.1'", 'max_digits': '5', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_discount': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bonus_order_set'", 'null': 'True', 'to': "orm['catalog.Order']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'catalog.container': {
            'Meta': {'object_name': 'Container'},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_container_set'", 'null': 'True', 'to': "orm['catalog.Container']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mean_rating': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'container_owner_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'container_service_set'", 'to': "orm['catalog.Service']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.item': {
            'Meta': {'object_name': 'Item'},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'item_container_set'", 'to': "orm['catalog.Container']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_special': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_special_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'special_cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'special_expires': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 20, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.offlineclient': {
            'Meta': {'object_name': 'OfflineClient'},
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'building': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offline_client_city'", 'to': "orm['geo.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'need_change': ('django.db.models.fields.DecimalField', [], {'default': '100', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'catalog.order': {
            'Meta': {'object_name': 'Order'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_client_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_container_set'", 'to': "orm['catalog.Container']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'deliver_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'deliver_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deliver_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offline_client': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_offline_client_set'", 'null': 'True', 'to': "orm['catalog.OfflineClient']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_service_set'", 'null': 'True', 'to': "orm['catalog.Service']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_confirmed'", 'max_length': '16'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'catalog.ordercontainer': {
            'Meta': {'object_name': 'OrderContainer'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ct_set_for_ordercontainer'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_container_order_set'", 'to': "orm['catalog.Order']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_order_container_set'", 'null': 'True', 'to': "orm['catalog.OrderContainer']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2'})
        },
        'catalog.service': {
            'Meta': {'object_name': 'Service'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.serviceterm': {
            'Meta': {'unique_together': "(('service', 'code'),)", 'object_name': 'ServiceTerm'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'service_term_set'", 'to': "orm['catalog.Service']"}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'catalog.vote': {
            'Meta': {'object_name': 'Vote'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_client_set'", 'to': "orm['auth.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "u'No comment provided'", 'max_length': '1024'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'vote_voteitem_set'", 'null': 'True', 'to': "orm['catalog.VoteItem']"}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_order_set'", 'to': "orm['catalog.Order']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_service_set'", 'null': 'True', 'to': "orm['catalog.Service']"}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'catalog.voteatom': {
            'Meta': {'object_name': 'VoteAtom'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voteatom_voteklass_set'", 'to': "orm['catalog.VoteKlass']"}),
            'max': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10'}),
            'min': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.voteitem': {
            'Meta': {'object_name': 'VoteItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voteitem_voteklass_set'", 'to': "orm['catalog.VoteKlass']"}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'voteitem_votelinks_sets'", 'symmetrical': 'False', 'to': "orm['catalog.VoteLink']"}),
            'mean': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        'catalog.voteklass': {
            'Meta': {'object_name': 'VoteKlass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voteklass_service_set'", 'to': "orm['catalog.Service']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.votelink': {
            'Meta': {'object_name': 'VoteLink'},
            'atom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votelink_voteatom_set'", 'to': "orm['catalog.VoteAtom']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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

    complete_apps = ['catalog']