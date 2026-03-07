from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
User = get_user_model()
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        '''
        Verify both passwords match.
        '''
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'active', 'admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class GuestForm(forms.Form):
    email = forms.EmailField()
    
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)


# Registro de Cliente Novo
#==========================================================================================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CustomerProfile

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=False, label='Sobrenome')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']  # email é login

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = f"{self.cleaned_data.get('first_name')} {self.cleaned_data.get('last_name')}".strip()
        if commit:
            user.save()
            # cria perfil automaticamente, caso queira armazenar telefone/endereço depois
            CustomerProfile.objects.get_or_create(user=user, user_type='cliente')
        return user