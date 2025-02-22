from django import forms
from .models import Task, Kanban
from django.conf import settings


class TaskAddForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'image']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image': f'Изображение, не больше {settings.IMAGE_MAX_SIZE_MB}мб',
        }


class KanbanAddForm(forms.ModelForm):
    class Meta:
        model = Kanban
        fields = ['title']
        labels = {'title': 'Название'}