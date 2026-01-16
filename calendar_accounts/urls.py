from django.urls import path
from calendar_accounts.views import manage_permissions, StrictLoginView

urlpatterns = [
    path('manage/<int:user_id>/', manage_permissions, name='manage_permissions'),
    path('login/', StrictLoginView.as_view(), name='login')
]