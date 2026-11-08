from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario


#formulario de registro 
class RegistroForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Usuario

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]

        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }

        help_texts = {
            'email': 'Utiliza un correo que no esté registrado.',
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Ejemplo: mily',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ejemplo: nombre@correo.com',
            }),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo electrónico.'
            )

        return email



class IngresoForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Escribe tu nombre de usuario',
        })


class PerfilForm(forms.ModelForm):

    class Meta:
        model = Usuario

        fields = [
            'first_name',
            'last_name',
            'email',
        ]

        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }

        help_texts = {
            'email': 'El correo no puede pertenecer a otra cuenta.',
        }

        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ejemplo: nombre@correo.com',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        otras_cuentas = Usuario.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        )

        if otras_cuentas.exists():
            raise forms.ValidationError(
                'Ya existe otra cuenta con este correo electrónico.'
            )

        return email