#:coding=utf8:

import uuid
import os

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from sorl.thumbnail import ImageField

from datetime import datetime

BLOG_LOCALES = (
    ('jp', u'日本語'),
    ('en', u'English'),
)

class PostManager(models.Manager):
    def published(self):
        return self.filter(pub_date__lt = datetime.now(), active=True)

class Post(models.Model):
    author = models.ForeignKey(User, verbose_name=u"author")
    slug = models.SlugField(u"slug", max_length=50, unique=True, db_index=True)
    title = models.TextField(u"title")
    lead = models.TextField(u"lead", blank=True, null=True, default=None, max_length=600)
    lead_image = ImageField(verbose_name="lead image", null=True, blank=True,
        upload_to=lambda instance, filename: 'thumbs/%s%s' % (
            uuid.uuid4().hex,
            os.path.splitext(filename)[1].lower(),
        ),
    )
    content = models.TextField(u"content")
    markup_type = models.CharField(max_length=10, choices=(
        ("md", "Markdown"),
        ("rst", "reStructuredText"),
        ("html", "HTML"),
    ), default="md")
    locale = models.CharField(u'locale', max_length=20, choices=BLOG_LOCALES, default="en", db_index=True)
    tags = TagField()

    active = models.BooleanField(u'published', default=False, db_index=True)
    pub_date = models.DateTimeField(u'published', default=datetime.now, db_index=True)
    create_date = models.DateTimeField(u'created', default=datetime.now)

    objects = PostManager()

    @models.permalink
    def get_absolute_url(self):
        return ('blog_detail', (), {
            'locale': self.locale,
            'slug': self.slug,
        })

    @property
    def lang(self):
        return {
            "en": "en",
            "jp": "ja",
        }.get(self.locale, "en")
    
    def get_full_url(self):
        return 'http://%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ('-pub_date',)
