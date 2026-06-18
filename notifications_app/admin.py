from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['to_user', 'is_read', 'is_seen', 'registers_id', 'register_type', 'extra_id', 'created_at', 'created_by']
    search_fields = [ 'to_user', 'registers_id', 'register_type', 'created_by'  ]

admin.site.register(Notification, NotificationAdmin)


