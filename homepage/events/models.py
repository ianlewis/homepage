#:coding=utf8:

from django.db import models
from datetime import date

class Event(models.Model):
    """
    An event
    """
    name = models.CharField('name', max_length=100)
    location = models.CharField('location', max_length=100)
    event_website = models.URLField(u'event url', blank=True, null=True, default=None)
    start_date = models.DateField(u'event start date', default=date.today,
                                    db_index=True)
    end_date = models.DateField(u'event end date', default=date.today)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ['-start_date']

class Talk(models.Model):
    """
    An talk
    """
    title = models.CharField('title', max_length=100)
    slug = models.SlugField(u"slug", max_length=150, unique=True, db_index=True)
    abstract = models.TextField(u'abstract')
    event = models.ForeignKey(Event, verbose_name=u"event")
    date = models.DateField(u'talk date', default=date.today,
                                    db_index=True)
    permalink = models.URLField(u'talk url', blank=True, null=True, default=None)
    video = models.URLField(u'video url', blank=True, null=True, default=None)
    slides = models.URLField(u'slides url', blank=True, null=True, default=None)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('talk_detail', (), {
            'slug': self.slug,
        })

    class Meta:
        verbose_name = "talk"
        verbose_name_plural = "talk"
        ordering = ['-date']
