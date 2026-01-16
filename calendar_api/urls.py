from django.urls import path, include
from rest_framework.routers import DefaultRouter
from calendar_api.views import EventViewSet, LoginView, RefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('doc/', SpectacularSwaggerView.as_view(), name='doc'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),
    path('token/', LoginView.as_view(), name='jwt_token'),
    path('token/refresh/', RefreshView.as_view(), name='jwt_refresh'),
]