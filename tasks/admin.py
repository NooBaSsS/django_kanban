from django.contrib import admin
from .models import Task, Kanban

admin.site.register(Task)
admin.site.register(Kanban)