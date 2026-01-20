from django.urls import path
from calendar_accounts.views import manage_permissions

urlpatterns = [
    path('manage/<int:user_id>/', manage_permissions, name='manage_permissions'),
]
