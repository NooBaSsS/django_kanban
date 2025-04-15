from os import rename
from uuid import uuid4

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Kanban(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="kanbans", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Канбан"
        verbose_name_plural = "Канбаны"


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, related_name="tasks", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tasks/img/", blank=True, null=True)
    kanban = models.ForeignKey(Kanban, related_name="tasks", on_delete=models.CASCADE)
    state_list = [
        ("PLANNED", "PLANNED"),
        ("IN_PROGRESS", "IN_PROGRESS"),
        ("REVIEW", "REVIEW"),
        ("DONE", "DONE"),
        ("OVERDUE", "OVERDUE"),
    ]
    state = models.CharField(default="PLANNED", choices=state_list, max_length=100)
    datetime_created = models.DateTimeField(default=timezone.now, editable=False)
    datetime_assigned = models.DateTimeField(null=True, blank=True)
    datetime_deadline = models.DateTimeField(null=True, blank=True)
    datetime_review = models.DateTimeField(null=True, blank=True)
    datetime_done = models.DateTimeField(null=True, blank=True)
    datetime_last_update = models.DateTimeField(default=timezone.now)
    datetime_deadline = models.DateTimeField(null=True, blank=True)
    executor = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def delete(self, *args, **kwargs):  # FIXME: если файл удален то FileNotFoundError
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def save(self):
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
            raise ValidationError(f"Изображение больше {settings.IMAGE_MAX_SIZE_MB}мб")

        return self.image

    def resize_image(self):
        img = Image.open(self.image.path)
        if max(img.width, img.height) <= settings.IMAGE_MAX_SIDE_PX:
            return
        img.thumbnail(
            (settings.IMAGE_MAX_SIDE_PX, settings.IMAGE_MAX_SIDE_PX), Image.LANCZOS
        )
        img.save(self.image.path)

    def rename_image(self):
        img_ext = self.image.path.split(".")[-1]
        new_image_name = str(uuid4()) + "." + img_ext
        new_image_path = f"{settings.MEDIA_ROOT}/tasks/img/{new_image_name}"
        rename(self.image.path, new_image_path)
        self.image.name = new_image_path

    def convert_img_to_jpg(self):
        img = Image.open(self.image.path)
        if img.format.upper() == "JPEG":
            return
        new_img_path = "".join(self.image.path.split(".")[:-1]) + ".jpg"
        new_img = img.convert("RGB")
        new_img.save(new_img_path, format="JPEG", quality=90)
        self.image.delete(save=False)
        self.image.name = new_img_path.split("/")[-1]

    def to_assigned(self):
        if not self.executor:
            raise ValueError("Назначьте исполнителя")
        if not self.datetime_deadline:
            raise ValueError("Укажите срок выполнения")
        if self.datetime_deadline < timezone.now():
            raise ValueError("Срок выполнения не может быть в прошлом")
        if self.state == "IN_PROGRESS":
            raise ValueError("Задача уже назначена")
        if self.state not in ("PLANNED", "REVIEW"):
            raise ValidationError(
                "Назначить можно только планируемую задачу или задачу на проверке"
            )

        self.state = "IN_PROGRESS"
        self.datetime_assigned = timezone.now()
        self.save()

    def to_review(self):
        if self.state != "IN_PROGRESS":
            raise ValidationError("На проверку можно взять только назначенную задачу")
        self.state = "REVIEW"
        self.datetime_review = timezone.now()
        self.save()

    def to_done(self):
        if self.state != "REVIEW":
            raise ValidationError("Выполнить можно только задачи на проверке")
        self.state = "DONE"
        self.datetime_done = timezone.now()
        self.save()

    def to_planned(self):
        self.state = "PLANNED"
        self.executor = None
        self.datetime_assigned = None
        self.datetime_deadline = None
        self.save()

    @classmethod
    def to_overdue(cls):
        now = timezone.now()
        overdue_tasks = cls.objects.filter(
            state="IN_PROGRESS",
            datetime_deadline__lte=now,
        )
        overdue_tasks.update(state="OVERDUE")
