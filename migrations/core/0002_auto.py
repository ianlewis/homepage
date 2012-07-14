# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Log', fields ['level']
        db.create_index('homepage_log', ['level'])

        # Adding index on 'Log', fields ['source']
        db.create_index('homepage_log', ['source'])

        # Adding index on 'Log', fields ['host']
        db.create_index('homepage_log', ['host'])


    def backwards(self, orm):
        
        # Removing index on 'Log', fields ['host']
        db.delete_index('homepage_log', ['host'])

        # Removing index on 'Log', fields ['source']
        db.delete_index('homepage_log', ['source'])

        # Removing index on 'Log', fields ['level']
        db.delete_index('homepage_log', ['level'])


    models = {
        'homepage.log': {
            'Meta': {'object_name': 'Log'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'host': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {}),
            'source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['homepage']
