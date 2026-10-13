from django.contrib import admin

from apps.shortener.models import URL, URLCollection, ShortURL


@admin.register(URLCollection)
class URLCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__email')
    list_select_related = ('user',)
    raw_id_fields = ('user',)


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'user', 'collection', 'created_at')
    search_fields = ('name', 'url', 'user__email')
    list_select_related = ('user', 'collection')
    raw_id_fields = ('user', 'collection')


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'url', 'is_active', 'created_at')
    search_fields = ('short_url', 'url__url', 'url__user__email')
    list_filter = ('is_active',)
    list_select_related = ('url__collection',)
    raw_id_fields = ('url',)
