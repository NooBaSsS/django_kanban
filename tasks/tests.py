from django.test import TestCase
from .models import Task
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path


# Create your tests here.
class TaskListTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="Test usr", password="123")
        self.task = Task.objects.create(
            title="Test task", description="Test desc", owner=owner
        )

    def test_task_list_view_authenticated(self):
        self.client.login(username="Test usr", password="123")
        response = self.client.get(reverse("tasks:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task)
        self.assertTemplateUsed(response, "tasks/list.html")

    def test_task_list_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("tasks:list"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "tasks/forbidden.html")

    def test_task_detail_view_authenticated(self):
        self.client.login(username="Test usr", password="123")
        response = self.client.get(reverse("tasks:detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task)
        self.assertTemplateUsed(response, "tasks/detail.html")

    def test_task_delete_view_authenticated(self):
        self.client.login(username="Test usr", password="123")
        response = self.client.post(reverse("tasks:delete", args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        task = Task.objects.filter(pk=self.task.pk)
        self.assertFalse(task.exists())

    def test_task_update_view_authenticated(self):
        self.client.login(username="Test usr", password="123")
        context = {"title": "123", "description": "321"}
        response = self.client.post(
            reverse("tasks:update", args=[self.task.pk]), context
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.title, context["title"])
        self.assertEqual(self.task.description, context["description"])

    def test_task_create_view_authenticated(self):
        self.client.login(username="Test usr", password="123")
        context = {"title": "123", "description": "321"}
        response = self.client.post(reverse("tasks:add"), context)
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        task = Task.objects.filter(title=context["title"])
        self.assertTrue(task.exists)


class TaskFormTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="Test usr", password="123")
        self.task = Task.objects.create(
            title="Test task", description="Test desc", owner=owner
        )


class TaskAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test usr",
            password="123",
        )

    def test_login(self):
        response = self.client.post(
            reverse("tasks:login"), {"username": "Test usr", "password": "123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username="Test usr", password="123")
        response = self.client.post(reverse("tasks:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TaskModelTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="Test usr",
            password="123",
        )
        self.task = Task.objects.create(
            title="Test task",
            description="Test desc",
            owner=owner,
        )

    def test_task_str(self):
        self.assertEqual(str(self.task), self.task.title)

    def test_task_image_upload(self):
        self.task.image = SimpleUploadedFile("testImg.jpg", b"", "image/jpg")
        self.task.save()
        img_path = self.task.image.path
        self.assertTrue(Path(img_path).exists())
        self.task.delete()

    def test_task_img_delete(self):
        self.task.image = SimpleUploadedFile("testImg.jpg", b"", "image/jpg")
        self.task.save()
        img_path = Path(self.task.image.path)
        self.task.delete()
        self.assertFalse(img_path.exists())

    def test_task_owner_delete(self):
        task = Task.objects.filter(pk=self.task.pk)
        self.task.owner.delete()
        self.assertFalse(task.exists())

