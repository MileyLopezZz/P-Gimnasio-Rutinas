from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DisciplinaForm, EquipamientoForm, RutinaForm
from .models import Disciplina, Equipamiento, Rutina


def _es_entrenador(usuario):
    return usuario.is_authenticated and usuario.rol == usuario.Rol.ENTRENADOR


def _rutina_del_entrenador_o_403(request, pk):
    """Devuelve la rutina solo si pertenece al usuario autenticado."""
    rutina = get_object_or_404(
        Rutina.objects.select_related('disciplina', 'entrenador').prefetch_related(
            'equipamientos'
        ),
        pk=pk,
    )
    if rutina.entrenador_id != request.user.id:
        raise PermissionDenied(
            'Solo el entrenador propietario puede modificar esta rutina.'
        )
    return rutina


@login_required
def rutina_crear(request):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores pueden crear rutinas.')

    if request.method == 'POST':
        form = RutinaForm(request.POST)
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.entrenador = request.user
            rutina.save()
            form.save_m2m()
            messages.success(request, 'La rutina se creó correctamente.')
            return redirect('mis_registros')
    else:
        form = RutinaForm()

    return render(request, 'P_gimnasio/rutina_form.html', {
        'form': form,
        'titulo_pagina': 'Crear rutina',
        'boton': 'Crear rutina',
    })


@login_required
def rutina_editar(request, pk):
    rutina = _rutina_del_entrenador_o_403(request, pk)

    if request.method == 'POST':
        form = RutinaForm(request.POST, instance=rutina)
        if form.is_valid():
            form.save()
            messages.success(request, 'La rutina se actualizó correctamente.')
            return redirect('mis_registros')
    else:
        form = RutinaForm(instance=rutina)

    return render(request, 'P_gimnasio/rutina_form.html', {
        'form': form,
        'rutina': rutina,
        'titulo_pagina': 'Editar rutina',
        'boton': 'Guardar cambios',
    })


@login_required
def rutina_eliminar(request, pk):
    rutina = _rutina_del_entrenador_o_403(request, pk)

    if request.method != 'POST':
        return render(request, 'P_gimnasio/rutina_confirmar_eliminar.html', {
            'rutina': rutina,
        })

    titulo = rutina.titulo
    rutina.delete()
    messages.success(request, f'La rutina «{titulo}» se eliminó correctamente.')
    return redirect('mis_registros')


@login_required
def mis_registros(request):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores tienen registros propios.')

    rutinas = (
        Rutina.objects.filter(entrenador=request.user)
        .select_related('disciplina')
        .prefetch_related('equipamientos')
    )
    return render(request, 'P_gimnasio/mis_registros.html', {
        'rutinas': rutinas,
    })


@login_required
def disciplina_crear(request):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores pueden crear catálogos.')

    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(
                request,
                f'La disciplina «{disciplina.nombre}» se creó correctamente.',
            )
            return redirect('rutina_crear')
    else:
        form = DisciplinaForm()

    return render(request, 'P_gimnasio/catalogo_form.html', {
        'form': form,
        'tipo_catalogo': 'disciplina',
        'titulo_pagina': 'Crear disciplina',
        'boton': 'Crear disciplina',
        'volver_url': 'rutina_crear',
    })


@login_required
def equipamiento_crear(request):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores pueden crear etiquetas.')

    if request.method == 'POST':
        form = EquipamientoForm(request.POST)
        if form.is_valid():
            equipamiento = form.save()
            messages.success(
                request,
                f'El equipamiento «{equipamiento.nombre}» se creó correctamente.',
            )
            return redirect('rutina_crear')
    else:
        form = EquipamientoForm()

    return render(request, 'P_gimnasio/catalogo_form.html', {
        'form': form,
        'tipo_catalogo': 'equipamiento',
        'titulo_pagina': 'Crear equipamiento',
        'boton': 'Crear equipamiento',
        'volver_url': 'rutina_crear',
    })


def rutina_detalle(request, pk):
    rutina = get_object_or_404(
        Rutina.objects.select_related('disciplina', 'entrenador').prefetch_related(
            'equipamientos'
        ),
        pk=pk,
    )
    return render(request, 'P_gimnasio/rutina_detalle.html', {'rutina': rutina})