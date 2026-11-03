from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import (
    Usuario,
    Disciplina,
    Equipamiento,
    Rutina,
    Inscripcion,
)


# ==========================================================
# FORMULARIO DE RUTINAS PARA EL ADMINISTRADOR
# ==========================================================
class RutinaAdminForm(forms.ModelForm):

    class Meta:
        model = Rutina
        fields = '__all__'

    def clean_equipamientos(self):
        # Obtiene los equipamientos seleccionados.
        equipamientos = self.cleaned_data.get('equipamientos')

        # No permite seleccionar más de cinco.
        if equipamientos is not None:
            if equipamientos.count() > 5:
                raise forms.ValidationError(
                    'Puedes seleccionar como máximo cinco equipamientos.'
                )

        return equipamientos


# ==========================================================
# USUARIOS
# ==========================================================
class UsuarioAdmin(UserAdmin):

    # Columnas visibles en el listado.
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'rol',
        'is_staff',
    )

    # Filtros que aparecen al costado.
    list_filter = (
        'rol',
        'is_staff',
        'is_active',
    )

    # Campos donde buscará la barra de búsqueda.
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    # Agrega el rol al formulario para editar usuarios.
    # El signo + conserva las secciones originales de Django.
    fieldsets = UserAdmin.fieldsets + (
        ('Rol en el gimnasio', {
            'fields': ('rol',),
        }),
    )

    # Agrega estos campos al formulario para crear usuarios.
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del gimnasio', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'rol',
            ),
        }),
    )


# ==========================================================
# DISCIPLINAS
# ==========================================================
class DisciplinaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
    )

    list_filter = (
        'nombre',
    )

    search_fields = (
        'nombre',
    )

    ordering = ('nombre',)


# ==========================================================
# EQUIPAMIENTOS
# ==========================================================
class EquipamientoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
    )

    list_filter = (
        'nombre',
    )

    search_fields = (
        'nombre',
    )

    ordering = ('nombre',)


# ==========================================================
# RUTINAS
# ==========================================================
class RutinaAdmin(admin.ModelAdmin):

    # Utiliza el formulario que limita los equipamientos.
    form = RutinaAdminForm

    list_display = (
        'id',
        'titulo',
        'entrenador',
        'disciplina',
        'duracion',
        'cupos',
        'nivel',
        'fecha_creacion',
    )

    list_filter = (
        'nivel',
        'disciplina',
        'entrenador',
    )

    search_fields = (
        'titulo',
        'descripcion',

        # Los dos guiones bajos permiten buscar
        # en un campo del modelo relacionado.
        'entrenador__username',
    )

    # Muestra un selector con dos cuadros para equipamientos.
    filter_horizontal = ('equipamientos',)

    # La fecha se muestra, pero no se puede modificar.
    readonly_fields = ('fecha_creacion',)

    # Carga estas relaciones junto con las rutinas
    # para evitar consultas repetidas al mostrar el listado.
    list_select_related = (
        'entrenador',
        'disciplina',
    )


# ==========================================================
# INSCRIPCIONES
# ==========================================================
class InscripcionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'rutina',
        'socio',
        'estado',
        'fecha_creacion',
    )

    list_filter = (
        'estado',
        'rutina',
    )

    search_fields = (
        'rutina__titulo',
        'socio__username',
        'comentario',
    )

    readonly_fields = ('fecha_creacion',)

    list_select_related = (
        'rutina',
        'socio',
    )


# ==========================================================
# REGISTRO DE LOS MODELOS
# Hace que aparezcan en el panel de administración.
# ==========================================================
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(Equipamiento, EquipamientoAdmin)
admin.site.register(Rutina, RutinaAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)


# Textos de la cabecera del administrador.
admin.site.site_header = 'Administración del gimnasio'
admin.site.site_title = 'Gimnasio'
admin.site.index_title = 'Gestión de datos'