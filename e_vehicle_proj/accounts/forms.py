import django.contrib.auth as auth

class AppUserCreationForm(auth.forms.UserCreationForm):

    class Meta(auth.forms.UserCreationForm.Meta):
        model = auth.get_user_model()  # set the user type to customer user type (models.AppUser)
        # origin fields would be ('username', 'password1', 'password2')
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = 'Optional. Only used to send password reset emails.'
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True

class AppUserAuthenticationForm(auth.forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Wrong username or password'
