from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission

User = get_user_model()


class UserPermissionsForm(forms.Form):
    readonly_fiedls_if_cant_manage = [
        'permissions'
    ]
    permissions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    extra_field = forms.CharField(required=False)

    def __init__(self, *args, user=None, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.manager = manager
        permissions = Permission.objects.all()
        self.fields['permissions'].choices = [
            (perm.id, f'{perm.content_type.app_label}.{perm.codename} - {perm.name}')
            for perm in permissions.order_by('content_type__app_label', 'codename')
        ]
        can_manage = self.manager.has_perm('calendar_accounts.can_manage_users') if self.manager else False
        if self.user:
            user_permissions = self.user.user_permissions.values_list('id', flat=True)
            self.fields['permissions'].initial = list(user_permissions)

        if not can_manage:
            self._readonly_view()

    def _readonly_view(self):
        for field in self.readonly_fiedls_if_cant_manage:
            self.fields[field].disabled = True


class CalendarUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'cell_phone', 'password1', 'password2')