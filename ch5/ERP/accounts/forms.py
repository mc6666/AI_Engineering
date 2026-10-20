from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

User = get_user_model()


class BootstrapFormMixin:
    """Adds the 'form-control' class expected by AdminLTE/Bootstrap to every field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class ChangePasswordForm(BootstrapFormMixin, PasswordChangeForm):
    pass
