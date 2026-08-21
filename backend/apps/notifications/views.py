from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Reminder, NotificationLog


@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(vehicle__user=request.user).select_related('vehicle')
    return render(request, 'notifications/reminders.html', {'reminders': reminders})


@login_required
def notification_history(request):
    logs = NotificationLog.objects.filter(vehicle__user=request.user).select_related('vehicle')
    return render(request, 'notifications/history.html', {'logs': logs})
