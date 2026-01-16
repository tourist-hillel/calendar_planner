# import pytest
# import django
# from django.conf import settings

# def pytest_configure():
#     settings.configure(
#         DEBUG = True,
#         SECRET_KEY = 'my-secret-key',
#         ALLOWED_HOSTS =['*'],
#         DATABASES = {
#             'default': {
#                 'ENGINE': 'django.db.backends.sqlite3',
#                 'NAME': ':memory'
#             }
#         },
#         INSTALLED_APPS = [
#             'django.contrib.admin',
#             'django.contrib.auth',
#             'django.contrib.contenttypes',
#             'django.contrib.sessions',
#             'django.contrib.messages',
#             'django.contrib.staticfiles',
#             'rest_framework',
#             'rest_framework.authtoken',
#             'rest_framework_simplejwt',
#             'drf_spectacular',
#             'events.apps.EventsConfig',
#             'categories.apps.CategoriesConfig',
#             'calendar_accounts.apps.CalendarAccountsConfig',
#             'calendar_api.apps.CalendarApiConfig',
#         ],
#         MIDDLEWARE = [
#             'django.middleware.security.SecurityMiddleware',
#             'django.contrib.sessions.middleware.SessionMiddleware',
#             'django.middleware.common.CommonMiddleware',
#             'django.middleware.csrf.CsrfViewMiddleware',
#             'django.contrib.auth.middleware.AuthenticationMiddleware',
#             'django.contrib.messages.middleware.MessageMiddleware',
#             'django.middleware.clickjacking.XFrameOptionsMiddleware',
#         ],
#         ROOT_URLCONF = 'calendar_planner.urls',
#         USE_TZ = True,
#         TIMEZONE = 'UTC',
#         REST_FRAMEWORK = {
#             'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
#             'DEFAULT_AUTHENTICATION_CLASSES': [
#                 'calendar_api.authentication.CalendarAppJWTAuthentication',
#                 # 'rest_framework_simplejwt.authentication.JWTAuthentication'
#             ],
#             'DEFAULT_PERMISSION_CLASSES': [
#                 'rest_framework.permissions.IsAuthenticated',
#             ]
#         }
#     )

#     django.setup()