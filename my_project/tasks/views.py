from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    TemplateView,
)
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .forms import TaskAddForm
from .models import Task

tasks = [i for i in range(1, 11)]


class AppWelcomeScreen(TemplateView):
    template_name = 'tasks/index.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

class TaskListView(UserPassesTestMixin, ListView):
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'

    def test_func(self) -> bool:
        return self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Для просмотра задач войдите или зарегистрирутесь'})
        )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(owner=self.request.user)
        return Task.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

class TaskDetailView(UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'

    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Вам нельзя просматривать эту задачу'})
        )


class TaskCreateView(UserPassesTestMixin, CreateView):
    model = Task
    form_class = TaskAddForm
    template_name = 'tasks/add.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self) -> bool:
        return self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Перед созданием задачи авторизуйтесь'})
        )


class TaskDeleteView(UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks:list')

    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Вам нельзя удалять эту задачу'})
        )


class TaskUpdateView(UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks:list')
    form_class = TaskAddForm

    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Вам нельзя редактировать эту задачу'})
        )


class AppLoginView(UserPassesTestMixin, LoginView):
    template_name = 'tasks/login.html'

    def get_success_url(self) -> str:
        return reverse_lazy('tasks:list')

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        raise PermissionDenied


class AppLogoutView(LogoutView):
    next_page = reverse_lazy('tasks:index')


class AppSignupView(UserPassesTestMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'tasks/signup.html'
    success_url = reverse_lazy('tasks:list')

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(self.request, 'tasks/forbidden.html', {'message': 'Вы уже авторизованы'})
        )