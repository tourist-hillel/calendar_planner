from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UsernameField
from calendar_accounts.models import CalendarUser
from django.contrib.contenttypes.models import ContentType


User = get_user_model()
admin.site.register(ContentType)


class CreationForm(BaseUserCreationForm):
    class Meta:
        model = CalendarUser
        fields = ('cell_phone', 'email')
        field_classes = {'cell_phone': UsernameField}


@admin.register(CalendarUser)
class CalendarUserAdmin(BaseUserAdmin):
    list_display = ('cell_phone', 'email', 'full_name', 'is_active', 'is_superuser')
    ordering = ('-cell_phone',)
    # change_password_form = AdminPasswordChangeForm
    add_form = CreationForm
    search_fields = ('cell_phone', 'first_name', 'last_name')

    add_fieldsets = (
        (None, {
            'classes': 'wide',
            'fields': ('cell_phone', 'email', 'password1', 'password2')
        }),
    )
    # fields = ['cell_phone', 'email', 'password1', 'password2']

    fieldsets = (
        (None, {'fields': ('cell_phone', 'email', 'is_active')}),
        ('Change password', {'fields': ('password',), 'classes': ('collapse',)}),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)
        }),
        ('Personal data', {'fields': (
            'first_name', 'last_name', 'date_of_birth', 'date_joined',
            'last_login', 'password_changed_at', 'profile_image',
            'failed_login_attempts', 'account_locked_until'
        ), 'classes': ('wide',)}),
        ('User settings', {'fields': ('preffered_lang',), 'classes': ('collapse',)}),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full name'
