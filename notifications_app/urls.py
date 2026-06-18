from django.urls import path
from notifications_app import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('notifications/<int:notification>/<int:extra_id>', views.view_notification, name='view_notification'),
    path('clear_notification/', views.clear_notification, name='clear_notification')
]