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

from .models import Disciplina, Equipamiento, Inscripcion, Rutina


class RutinaForm(forms.ModelForm):
    """Formulario público para crear y editar rutinas."""

    class Meta:
        model = Rutina
        fields = [
            'titulo',
            'descripcion',
            'duracion',
            'cupos',
            'nivel',
            'disciplina',
            'equipamientos',
        ]
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'duracion': 'Duración en minutos',
            'cupos': 'Cupos disponibles',
            'nivel': 'Nivel',
            'disciplina': 'Disciplina',
            'equipamientos': 'Equipamiento',
        }
        help_texts = {
            'duracion': 'Debe estar entre 10 y 120 minutos.',
            'cupos': 'Debe estar entre 1 y 30 cupos.',
            'equipamientos': 'Puedes seleccionar hasta cinco etiquetas.',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
            'equipamientos': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disciplina'].queryset = Disciplina.objects.order_by('nombre')
        self.fields['disciplina'].empty_label = '— Sin disciplina —'
        self.fields['equipamientos'].queryset = Equipamiento.objects.order_by('nombre')

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 5:
            raise forms.ValidationError(
                'El título debe tener al menos 5 caracteres.'
            )
        return titulo

    def clean_equipamientos(self):
        equipamientos = self.cleaned_data.get('equipamientos')
        if equipamientos is not None and equipamientos.count() > 5:
            raise forms.ValidationError(
                'Una rutina puede tener como máximo cinco equipamientos.'
            )
        return equipamientos


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nombre']
        labels = {'nombre': 'Nombre de la disciplina'}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        return nombre


class EquipamientoForm(forms.ModelForm):
    class Meta:
        model = Equipamiento
        fields = ['nombre']
        labels = {'nombre': 'Nombre del equipamiento'}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        return nombre


class InscripcionForm(forms.ModelForm):
    """El socio solo puede escribir un comentario al solicitar una rutina."""

    class Meta:
        model = Inscripcion
        fields = ['comentario']
        labels = {'comentario': 'Comentario para el entrenador (opcional)'}
        widgets = {
            'comentario': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Cuéntale algo al entrenador, si lo necesitas.',
            }),
        }
