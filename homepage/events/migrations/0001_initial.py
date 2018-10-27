# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-27 12:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name=b'name')),
                ('location', models.CharField(max_length=100, verbose_name=b'location')),
                ('event_website', models.URLField(blank=True, default=None, null=True, verbose_name='event url')),
                ('start_date', models.DateField(db_index=True, default=datetime.date.today, verbose_name='event start date')),
                ('end_date', models.DateField(default=datetime.date.today, verbose_name='event end date')),
            ],
            options={
                'ordering': ['-start_date'],
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name=b'title')),
                ('slug', models.SlugField(max_length=150, unique=True, verbose_name='slug')),
                ('abstract', models.TextField(verbose_name='abstract')),
                ('date', models.DateField(db_index=True, default=datetime.date.today, verbose_name='talk date')),
                ('permalink', models.URLField(blank=True, default=None, null=True, verbose_name='talk url')),
                ('video', models.URLField(blank=True, default=None, null=True, verbose_name='video url')),
                ('slides', models.URLField(blank=True, default=None, null=True, verbose_name='slides url')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event', verbose_name='event')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'talk',
                'verbose_name_plural': 'talk',
            },
        ),
    ]