from django import forms
from .models import Task, Kanban
from django.conf import settings


class TaskAddForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "image"]
        labels = {
            "title": "Название",
            "description": "Описание",
            "image": f"Изображение, не больше {settings.IMAGE_MAX_SIZE_MB}мб",
        }


class KanbanAddForm(forms.ModelForm):
    class Meta:
        model = Kanban
        fields = ["title"]
        labels = {"title": "Название"}


class TaskAssignForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["executor", "datetime_deadline"]
        labels = {
            "executor": "Исполнитель",
            "datetime_deadline": "Срок выполнения",
        }
        widgets = {
            "executor": forms.Select(attrs={"required": "True"}),
            "datetime_deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "required": "True"}
            ),
        }


class TaskReviewForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = []
        labels = {}
        widgets = {}


class TaskDoneForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = []
        labels = {}
        widgets = {}


class TaskOverdueForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = []
        labels = {}
        widgets = {}
