from django import forms

from .models import Disciplina, Equipamiento, Rutina


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