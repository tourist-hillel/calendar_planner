from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from calendar_accounts.forms import UserPermissionsForm

User = get_user_model()

@login_required
@permission_required('calendar_accounts.can_see_user_permissions', raise_exception=True)
def manage_permissions(request, user_id):
    form = None
    selected_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserPermissionsForm(request.POST, user=selected_user, manager=request.user)
        if form.is_valid():
            selected_user.user_permissions.clear()
            selected_permissions = form.cleaned_data['permissions']
            for perm_id in selected_permissions:
                permission = Permission.objects.get(id=perm_id)
                selected_user.user_permissions.add(permission)
            return redirect('manage_permissions', user_id=user_id)
    else:
        form = UserPermissionsForm(user=selected_user, manager=request.user)
    return render(request, 'manage_permissions.html', {'form': form})


class StrictLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login.html'
    success_view = 'event_list'
    login_attempt_fail_template = 'login_attempt_failed.html'
    

    def get_success_url(self) -> str:
        return self.success_view
    
    def _check_account_lock(self, user):
        if user.is_account_locked:
            return render(
                self.request,
                self.login_attempt_fail_template,
                {'locked_until': user.account_locked_until}
            )
    
    def form_invalid(self, form):
        try:
            user = User.objects.get(cell_phone=form.cleaned_data['username'])
            User.process_failed_login_attempt(user)
            user.refresh_from_db()
            self._check_account_lock(user)  
        except User.DoesNotExist:
            pass
        form.add_error(None, 'Невірний номер телефону або пароль!')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        user = form.get_user()
        self._check_account_lock(user)
        User.process_success_login_attempt(user)
        auth_login(self.request, user)
        return redirect(self.get_success_url())
    


