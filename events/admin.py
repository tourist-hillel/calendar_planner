from django.contrib import admin
from events.models import Event, EventLog


admin.site.register(Event)
admin.site.register(EventLog)
