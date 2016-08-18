#:coding=utf8:

from django.contrib import admin
from django.contrib.auth.models import User

from homepage.blog.models import Tag, Post


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "locale", "markup_type", "pub_date",
                    "active")
    list_filter = ("active", "locale", "markup_type")
    filter_horizontal = ('tags',)
    list_display_links = ("id", "title")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    actions = ['publish', 'unpublish']

    def publish(modeladmin, request, queryset):
        queryset.update(active=True)
    publish.short_description = "Publish selected posts"

    def unpublish(modeladmin, request, queryset):
        queryset.update(active=False)
    unpublish.short_description = "Un-publish selected posts"

    def get_form(self, request, obj=None, **kwargs):
        '''
        Overwrite get_form to select the currently logged in user as the author
        Copied from byteflow.
        '''
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        f = form.base_fields['author']
        f.initial = request.user.pk
        if request.user.is_superuser:
            f.queryset = User.objects.filter(is_staff=True)
        else:
            f.queryset = User.objects.filter(pk=request.user.pk)
        return form

admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
