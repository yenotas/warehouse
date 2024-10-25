from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.contrib.auth.models import Permission, Group
from django.contrib.admin.models import LogEntry

# Удаляем системные модели из админки
admin.site.unregister(ContentType)
admin.site.unregister(Session)
admin.site.unregister(Permission)
admin.site.unregister(Group)
admin.site.unregister(LogEntry)