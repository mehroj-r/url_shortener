from django.contrib import admin

from apps.analytics.models import URLClick


@admin.register(URLClick)
class URLClickAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'ipv4_address', 'ipv6_address', 'referer', 'created_at')
    search_fields = ('short_url__short_url', 'ipv4_address', 'referer')
    list_select_related = ('short_url__url',)
    raw_id_fields = ('short_url',)
    date_hierarchy = 'created_at'
