from django import forms
from .models import Task
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('image') is None and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if commit:
            instance.save()
        return instance
