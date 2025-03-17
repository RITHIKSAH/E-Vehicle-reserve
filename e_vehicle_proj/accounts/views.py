from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
import django.contrib.auth as auth
import django.contrib.auth.views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from .forms import AppUserCreationForm, AppUserAuthenticationForm


# a view inherits LoginView in django auth
class UserLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    form_class = AppUserAuthenticationForm

# a view based on UserCreationForm in django auth
class UserRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = AppUserCreationForm  # custom register form
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        # add user to customer group
        customer_group = auth.models.Group.objects.get(name='customer')
        user.groups.add(customer_group)
        auth.login(self.request, user)
        return super().form_valid(form)

# a view inherits templateview to show template redirect.html
class UserRedirectView(TemplateView):
    template_name = 'accounts/redirect.html'

    # get current user and send to template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context
    
# a view inherits logoutview in django auth
class UserLogoutView(auth_views.LogoutView):
    # after logged out, user will go to index page of this website
    # this logout.html is just an empty file and hopefully not to be shown to user
    template_name = 'accounts/logout.html'

# ==================== password reset part starts from here ====================
# this view inherits PasswordResetView in django auth
# it helps the user to reset password through email (when the user forget the password)
class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/pass_reset.html'
    email_template_name = 'accounts/pass_reset_email.txt'  # this is the email
    subject_template_name = 'accounts/pass_reset_subject.txt'  # this is the subject of email
    success_url = reverse_lazy('pass_reset_done')  # url for PasswordResetDoneView

# this view tells the user that the email is already sent
# in some cases though the email can be sent, but this page is still shown to user
class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/pass_reset_done.html'

# this view ask the user about the new password
class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/pass_reset_confirm.html'
    success_url = reverse_lazy('pass_reset_complete')  # url for PasswordResetCompleteView

# this view tells the user that the password has reset
class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/pass_reset_complete.html'
# ==================== password reset part ends here ====================

# ==================== password change part starts here ====================
class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/pass_change.html'
    success_url = reverse_lazy('pass_change_done')  # url for PasswordChangeDoneView
    
class UserPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'accounts/pass_change_done.html'
# ==================== password change part ends here ====================

class OperatorViewMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='operator').exists()
    
    def handle_no_permission(self):
        path = self.request.get_full_path()
        return redirect_to_login(next = path)

class ManagerViewMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='manager').exists()

    def handle_no_permission(self):
        path = self.request.get_full_path()
        return redirect_to_login(next = path)
    
def operator_group_check(user):
    return user.groups.filter(name='operator').exists()

def manager_group_check(user):
    return user.groups.filter(name='manager').exists()