from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image
from uuid import uuid4
from os import rename


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tasks/img/', blank=True, null=True)

    def __str__(self) -> str:
        return self.title

    def delete(self, *args, **kwargs): # FIXME: если файл удален то FileNotFoundError
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def save(self):
        '''
        TODO:
            тесты
            консистентное наименование файлов
            конвертировать все в jpg
        '''
        if self.pk:
            old_image = Task.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                old_image.delete(save=False)
        super().save()

        if self.image:
            self.resize_image()
            self.convert_img_to_jpg()
            self.rename_image()
            super().save()

    def clean(self):
        super().clean()
        if self.image:
            self.validate_image()

    def validate_image(self):
        if not self.image:
            return

        img = Image.open(self.image)
        width, height = img.size

        if self.image.size / 1024 / 1024 > settings.IMAGE_MAX_SIZE_MB:
            raise ValidationError(f'Изображение больше {settings.IMAGE_MAX_SIZE_MB}мб')

        return self.image

    def resize_image(self):
        img = Image.open(self.image.path)
        if max(img.width, img.height) <= settings.IMAGE_MAX_SIDE_PX:
            return
        img.thumbnail((settings.IMAGE_MAX_SIDE_PX, settings.IMAGE_MAX_SIDE_PX), Image.LANCZOS)
        img.save(self.image.path)

    def rename_image(self): # FIXME: починить отображение по новому имени
        img_ext = self.image.path.split('.')[-1]
        new_image_name = str(uuid4()) + '.' + img_ext
        new_image_path = f'{settings.MEDIA_ROOT}/tasks/img/{new_image_name}'
        rename(self.image.path, new_image_path)
        self.image.name = new_image_path

    def convert_img_to_jpg(self):
        img = Image.open(self.image.path)
        if img.format.upper() == 'JPEG':
            return
        new_img_path = ''.join(self.image.path.split('.')[:-1]) + '.jpg'
        new_img = img.convert('RGB')
        new_img.save(new_img_path, format='JPEG', quality=90)
        self.image.delete(save=False)
        self.image.name = new_img_path.split('/')[-1]

