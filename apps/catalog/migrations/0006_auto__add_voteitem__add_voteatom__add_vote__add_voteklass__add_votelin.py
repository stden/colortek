# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VoteItem'
        db.create_table('catalog_voteitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voteitem_voteklass_set', to=orm['catalog.VoteKlass'])),
        ))
        db.send_create_signal('catalog', ['VoteItem'])

        # Adding M2M table for field links on 'VoteItem'
        db.create_table('catalog_voteitem_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('voteitem', models.ForeignKey(orm['catalog.voteitem'], null=False)),
            ('votelink', models.ForeignKey(orm['catalog.votelink'], null=False))
        ))
        db.create_unique('catalog_voteitem_links', ['voteitem_id', 'votelink_id'])

        # Adding model 'VoteAtom'
        db.create_table('catalog_voteatom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voteatom_voteklass_set', to=orm['catalog.VoteKlass'])),
            ('min', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('max', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10)),
        ))
        db.send_create_signal('catalog', ['VoteAtom'])

        # Adding model 'Vote'
        db.create_table('catalog_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vote_order_set', to=orm['catalog.Order'])),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vote_client_set', to=orm['auth.User'])),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('items', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vote_voteitem_set', to=orm['catalog.VoteItem'])),
        ))
        db.send_create_signal('catalog', ['Vote'])

        # Adding model 'VoteKlass'
        db.create_table('catalog_voteklass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voteklass_service_set', to=orm['catalog.Service'])),
        ))
        db.send_create_signal('catalog', ['VoteKlass'])

        # Adding model 'VoteLink'
        db.create_table('catalog_votelink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('atom', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votelink_voteatom_set', to=orm['catalog.VoteAtom'])),
            ('value', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('catalog', ['VoteLink'])


    def backwards(self, orm):
        # Deleting model 'VoteItem'
        db.delete_table('catalog_voteitem')

        # Removing M2M table for field links on 'VoteItem'
        db.delete_table('catalog_voteitem_links')

        # Deleting model 'VoteAtom'
        db.delete_table('catalog_voteatom')

        # Deleting model 'Vote'
        db.delete_table('catalog_vote')

        # Deleting model 'VoteKlass'
        db.delete_table('catalog_voteklass')

        # Deleting model 'VoteLink'
        db.delete_table('catalog_votelink')


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
            'building': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['geo.City']"}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invites': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_partner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
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
        'catalog.order': {
            'Meta': {'object_name': 'Order'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_client_set'", 'to': "orm['auth.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '10', 'decimal_places': '2'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['catalog.Item']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'in progress'", 'max_length': '16'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'catalog.service': {
            'Meta': {'object_name': 'Service'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'catalog.vote': {
            'Meta': {'object_name': 'Vote'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_client_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_voteitem_set'", 'to': "orm['catalog.VoteItem']"}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote_order_set'", 'to': "orm['catalog.Order']"}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'voteitem_votelinks_sets'", 'symmetrical': 'False', 'to': "orm['catalog.VoteLink']"})
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