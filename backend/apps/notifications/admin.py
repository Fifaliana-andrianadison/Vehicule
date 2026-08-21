from django.contrib import admin
from .models import Reminder, NotificationLog


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'reminder_type', 'title', 'due_date', 'is_sent']
    list_filter = ['reminder_type', 'is_sent']
    search_fields = ['vehicle__name', 'title']
    date_hierarchy = 'due_date'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'sent_at', 'is_success']
    list_filter = ['is_success']
    date_hierarchy = 'sent_at'
