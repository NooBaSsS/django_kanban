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
from django.shortcuts import render, get_object_or_404
from .forms import (
    TaskAddForm,
    KanbanAddForm,
    TaskAssignForm,
    TaskReviewForm,
    TaskDoneForm,
)
from .models import Task, Kanban
from django.utils import timezone

tasks = [i for i in range(1, 11)]
"""
любой исполнитель одной задачи может видеть весь канбан
видеть список канбанов, в которых пользователь принимает участие
"""


class KanbanListView(UserPassesTestMixin, ListView):
    model = Kanban
    template_name = "tasks/kanban_list.html"
    context_object_name = "kanbans"

    def test_func(self) -> bool:
        return self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {
                    "error_message": "Для просмотра канбанов войдите или зарегистрирутесь"
                },
            )
        )

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return Kanban.objects.filter(owner=self.request.user)
        return Kanban.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_authenticated"] = self.request.user.is_authenticated
        return context


class AppWelcomeScreen(TemplateView):
    template_name = "tasks/index.html"
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_authenticated"] = self.request.user.is_authenticated
        return context


class TaskPermissionMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Вам нельзя просматривать эту задачу"},
            )
        )


class KanbanDetailView(UserPassesTestMixin, DetailView):
    model = Kanban
    template_name = "tasks/kanban_detail.html"
    context_object_name = "kanban"

    def test_func(self) -> bool:
        kanban = self.get_object()
        return kanban.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Вам нельзя просматривать эту доску"},
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks_planned"] = Task.objects.filter(state="PLANNED")
        context["tasks_assigned"] = Task.objects.filter(state="IN_PROGRESS")
        context["tasks_review"] = Task.objects.filter(state="REVIEW")
        context["tasks_done"] = Task.objects.filter(state="DONE")
        context["tasks_overdue"] = Task.objects.filter(state="OVERDUE")
        return context


class TaskDetailView(TaskPermissionMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class KanbanCreateView(UserPassesTestMixin, CreateView):
    model = Kanban
    form_class = KanbanAddForm
    template_name = "tasks/kanban_add.html"
    success_url = reverse_lazy("tasks:kanban_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self) -> bool:
        return self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Перед созданием канбана авторизуйтесь"},
            )
        )


class KanbanDeleteView(UserPassesTestMixin, DeleteView):
    model = Kanban
    template_name = "tasks/kanban_delete.html"
    success_url = reverse_lazy("tasks:kanban_list")

    def test_func(self) -> bool:
        kanban = self.get_object()
        return kanban.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Вам нельзя удалять этот канбан"},
            )
        )


class TaskCreateView(UserPassesTestMixin, CreateView):
    model = Task
    form_class = TaskAddForm
    template_name = "tasks/task_add.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.kanban = Kanban.objects.get(pk=self.kwargs["kanban_pk"])
        form.instance.state = "PLANNED"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:kanban_detail", kwargs={"pk": self.object.kanban.pk})

    def test_func(self) -> bool:
        return self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Перед созданием задачи авторизуйтесь"},
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kanban_pk"] = self.kwargs["kanban_pk"]
        return context


class TaskDeleteView(TaskPermissionMixin, DeleteView):
    model = Task
    template_name = "tasks/task_delete.html"

    def get_success_url(self):
        return reverse_lazy("tasks:kanban_detail", kwargs={"pk": self.object.kanban.pk})


class TaskUpdateView(TaskPermissionMixin, UpdateView):
    model = Task
    template_name = "tasks/task_update.html"
    form_class = TaskAddForm

    def get_success_url(self):
        return reverse_lazy("tasks:kanban_detail", kwargs={"pk": self.object.kanban.pk})


class TaskChangeStateBaseView(UserPassesTestMixin, UpdateView):
    model = Task
    form_class = None
    template_name = None

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:kanban_detail", kwargs={"pk": self.object.kanban.pk})

    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/error.html",
                {"error_message": "Вам нельзя изменять статус этой задачи"},
            )
        )

    def dispatch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        error_message = self.get_error_message(task)
        if error_message:
            return render(
                request,
                "tasks/error.html",
                {
                    "error_message": "Назначить можно только планируемую задачу "
                    "или задачу на проверке"
                },
            )
        return super().dispatch(request, *args, **kwargs)


class TaskAssignView(TaskChangeStateBaseView):
    form_class = TaskAssignForm
    template_name = "tasks/task_assign.html"

    def form_valid(self, form):  # в модель
        executor = form.cleaned_data["executor"]
        datetime_deadline = form.cleaned_data["datetime_deadline"]
        datetime_now = timezone.now()

        if not executor:
            form.add_error("executor", "Выберите исполнителя")
            return self.form_invalid(form)

        if datetime_deadline < datetime_now:
            form.add_error(
                "datetime_deadline", "Срок выполнения не может быть в прошлом"
            )
            return self.form_invalid(form)

        form.instance.to_assigned()
        return super().form_valid(form)

    def get_error_message(self, task: Task):
        if task.state not in ("PLANNED", "REVIEW"):
            error_message = (
                "Назначить можно только планируемую задачу или задачу на проверке"
            )
        else:
            error_message = ""
        return error_message


class TaskReviewView(TaskChangeStateBaseView):
    form_class = TaskReviewForm
    template_name = "tasks/task_review.html"

    def form_valid(self, form):
        form.instance.to_review()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        if task.state != "IN_PROGRESS":
            return render(
                request,
                "tasks/error.html",
                {"error_message": "На проверку можно взять только назначенные задачи"},
            )
        return super().dispatch(request, *args, **kwargs)

    def get_error_message(self, task: Task):
        if task.state != "IN_PROGRESS":
            error_message = "На проверку можно взять только назначенные задачи"
        else:
            error_message = ""
        return error_message


class TaskDoneView(TaskChangeStateBaseView):
    template_name = "tasks/task_done.html"
    form_class = TaskDoneForm

    def form_valid(self, form):
        form.instance.to_done()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        if task.state != "REVIEW":
            return render(
                request,
                "tasks/error.html",
                {"error_message": "Нельзя завершить задачу не на проверке"},
            )
        return super().dispatch(request, *args, **kwargs)

    def get_error_message(self, task: Task):
        if task.state != "REVIEW":
            error_message = "Нельзя завершить задачу не на проверке"
        else:
            error_message = ""
        return error_message


class TaskChangeStateView(UserPassesTestMixin, UpdateView):  #! Удалить
    model = Task
    template_name = "tasks/task_change_state.html"
    fields = []

    def form_valid(self, form):
        executor = form.cleaned_data["executor"]
        if not executor:
            form.add_error("executor", "Выберите исполнителя")
            return self.form_invalid(form)
        form.instance.to_assigned()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:kanban_detail", kwargs={"pk": self.object.kanban.pk})

    def test_func(self) -> bool:
        task = self.get_object()
        return task.owner == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request,
                "tasks/forbidden.html",
                {"message": "Вам нельзя изменять статус этой задачи"},
            )
        )


class AppLoginView(UserPassesTestMixin, LoginView):
    template_name = "tasks/login.html"

    def get_success_url(self) -> str:
        return reverse_lazy("tasks:kanban_list")

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        raise PermissionDenied


class AppLogoutView(LogoutView):
    next_page = reverse_lazy("tasks:index")


class AppSignupView(UserPassesTestMixin, CreateView):
    form_class = UserCreationForm
    template_name = "tasks/signup.html"
    success_url = reverse_lazy("tasks:kanban_list")

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseForbidden(
            render(
                self.request, "tasks/forbidden.html", {"message": "Вы уже авторизованы"}
            )
        )
