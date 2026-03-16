from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/latest-alert/', views.get_latest_alert, name='latest_alert'),
]