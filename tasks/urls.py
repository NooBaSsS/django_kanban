from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("kanban_list/", views.KanbanListView.as_view(), name="kanban_list"),
    path(
        "<int:pk>/kanban_detail/",
        views.KanbanDetailView.as_view(),
        name="kanban_detail",
    ),
    path("kanban_add/", views.KanbanCreateView.as_view(), name="kanban_add"),
    path(
        "<int:pk>/kanban_delete/",
        views.KanbanDeleteView.as_view(),
        name="kanban_delete",
    ),
    path("", views.AppWelcomeScreen.as_view(), name="index"),
    path("<int:kanban_pk>/task_add/", views.TaskCreateView.as_view(), name="task_add"),
    path("<int:pk>/task_delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("<int:pk>/task_update/", views.TaskUpdateView.as_view(), name="task_update"),
    path("<int:pk>/task_detail/", views.TaskDetailView.as_view(), name="task_detail"),
    path(
        "<int:pk>/task_change_state/",
        views.TaskChangeStateView.as_view(),
        name="task_change_state",
    ),
    path("<int:pk>/task_assign/", views.TaskAssignView.as_view(), name="task_assign"),
    path("<int:pk>/task_review/", views.TaskReviewView.as_view(), name="task_review"),
    path("<int:pk>/task_done/", views.TaskDoneView.as_view(), name="task_done"),
    path("login/", views.AppLoginView.as_view(), name="login"),
    path("logout/", views.AppLogoutView.as_view(), name="logout"),
    path("signin/", views.AppSignupView.as_view(), name="signup"),
]

