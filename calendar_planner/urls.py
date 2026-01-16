"""
URL configuration for calendar_planner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from events.views import register
from calendar_accounts.views import StrictLoginView

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('permissions/', include('calendar_accounts.urls')),
    path('api/', include('calendar_api.urls')),
    path('api/obtain_token/', TokenObtainPairView.as_view(), name='obtain_token'),
    path('api/refresh_token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('register/', register, name='register'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sentry-debug/', trigger_error),
    path(
        'reset-password/',
        auth_views.PasswordResetView.as_view(success_url='/reset-password/done/'),
        name='reset_password'
    ),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='reset_password_done'),
    path(
        'reset-password-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(success_url='/reset-password-complete/'),
        name='password_reset_confirm'
    ),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', StrictLoginView.as_view(), name='login')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

