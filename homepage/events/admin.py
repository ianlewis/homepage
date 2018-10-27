#:coding=utf8:

from django.contrib import admin

from homepage.events.models import Event, Talk


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "start_date", "end_date")
    list_filter = ("location",)
    list_display_links = ("id", "name")
    search_fields = ("title", "location")

class TalkAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "event", "date")
    list_filter = ("event",)
    list_display_links = ("id", "title")
    search_fields = ("title", "event__name", "event__location")
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Event, EventAdmin)
admin.site.register(Talk, TalkAdmin)

