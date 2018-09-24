# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('title', models.TextField(verbose_name='title')),
                ('lead', models.TextField(default=None, max_length=600, null=True, verbose_name='lead', blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('markup_type', models.CharField(default=b'md', max_length=10, choices=[(b'md', b'Markdown'), (b'rst', b'reStructuredText'), (b'html', b'HTML')])),
                ('locale', models.CharField(default=b'en', max_length=20, verbose_name='locale', db_index=True, choices=[(b'jp', '\u65e5\u672c\u8a9e'), (b'en', 'English')])),
                ('active', models.BooleanField(default=False, db_index=True, verbose_name='published')),
                ('pub_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='published', db_index=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('author', models.ForeignKey(verbose_name='author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name', db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='blog.Tag', blank=True),
        ),
    ]
