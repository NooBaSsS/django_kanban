from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.AppWelcomeScreen.as_view(), name='index'),
    path('list', views.TaskListView.as_view(), name='list'),
    path('add/', views.TaskCreateView.as_view(), name='add'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/detail/', views.TaskDetailView.as_view(), name='detail'),
    path('login/', views.AppLoginView.as_view(), name='login'),
    path('logout/', views.AppLogoutView.as_view(), name='logout'),
    path('signin/', views.AppSignupView.as_view(), name='signup'),
]