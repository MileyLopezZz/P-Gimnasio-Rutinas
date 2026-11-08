from django.shortcuts import render, get_object_or_404,redirect
from .models import Rutina,Disciplina,Inscripcion,Equipamiento
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .forms import RegistroForm, PerfilForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST

from .forms import (
    DisciplinaForm,
    EquipamientoForm,
    InscripcionForm,
    RutinaForm,
)


# Create your views here.

def inicio(request):
    rutinas_recientes=(
        Rutina.objects
        .select_related('disciplina','entrenador')
        .prefetch_related('equipamientos')
        .order_by('-fecha_creacion', '-id')[:4]
    )

    #contadores de la portada

    total_rutinas = Rutina.objects.count()
    total_disciplinas = Disciplina.objects.count()
    total_inscripciones_confirmadas = (
        Inscripcion.objects
        .filter(estado='confirmada')
        .count()
    )

    # datos visibles en el template
    contexto = {
        'rutinas_recientes': rutinas_recientes,
        'total_rutinas': total_rutinas,
        'total_disciplinas': total_disciplinas,
        'total_inscripciones_confirmadas': (total_inscripciones_confirmadas),
    }

    return render(request, 'inicio.html', contexto)




def lista_rutinas(request):
    # Leemos la búsqueda y la disciplina desde la dirección.
    q = request.GET.get('q', '').strip()
    disciplina_id = request.GET.get('disciplina', '').strip()

    # Estas disciplinas se mostrarán en el selector.
    disciplinas = Disciplina.objects.order_by('nombre')

    # Preparamos las rutinas con sus relaciones.
    qs = (
        Rutina.objects
        .select_related('disciplina', 'entrenador')
        .prefetch_related('equipamientos')
        .order_by('titulo', 'id')
    )

    # Buscamos en el título O en la descripción.
    if q:
        qs = qs.filter(
            Q(titulo__icontains=q) |
            Q(descripcion__icontains=q)
        )

    # Comprobamos que la disciplina recibida sea válida.
    error_filtro = ''

    if disciplina_id:
        ids_validos = {
            str(disciplina.pk)
            for disciplina in disciplinas
        }

        if disciplina_id in ids_validos:
            qs = qs.filter(disciplina_id=disciplina_id)
        else:
            qs = qs.none()
            error_filtro = 'La disciplina seleccionada no es válida.'

    # Mostramos cinco rutinas por página.
    paginador = Paginator(qs, 5)
    page_obj = paginador.get_page(request.GET.get('page'))

    # Conservamos la búsqueda y los filtros al cambiar de página.
    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    contexto = {
        'page_obj': page_obj,
        'q': q,
        'disciplinas': disciplinas,
        'disciplina_id': disciplina_id,
        'error_filtro': error_filtro,
        'querystring': querystring,
    }

    return render(request, 'lista_rutinas.html', contexto)


def detalle_rutina(request, pk):
    # Preparamos las relaciones que mostraremos en el detalle.
    consulta = (
        Rutina.objects
        .select_related('disciplina', 'entrenador')
        .prefetch_related('equipamientos')
    )

    # Buscamos la rutina por su identificador.
    rutina = get_object_or_404(consulta, pk=pk)

    contexto = {
        'rutina': rutina,
    }

    return render(request, 'detalle_rutina.html', contexto)



def registro(request):
    # Una persona que ya ingresó vuelve a la portada.
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Cuenta creada correctamente.'
            )

            return redirect('inicio')

    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


#///////////////////////

@login_required
def cuenta(request):
    return render(request, 'cuenta.html')


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = PerfilForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Perfil actualizado correctamente.'
            )

            return redirect('cuenta')

    else:
        form = PerfilForm(instance=request.user)

    return render(
        request,
        'editar_perfil.html',
        {'form': form},
    )



def _es_entrenador(usuario):
    return usuario.is_authenticated and usuario.rol == usuario.Rol.ENTRENADOR


def _es_socio(usuario):
    return usuario.is_authenticated and usuario.rol == usuario.Rol.SOCIO


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
def inicio_usuario(request):
    """Destino de inicio de sesión según el rol de la cuenta."""
    if _es_entrenador(request.user):
        return redirect('mis_registros')
    if _es_socio(request.user):
        return redirect('mis_solicitudes')
    raise PermissionDenied('La cuenta no tiene un rol válido en el gimnasio.')


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

    return render(request, 'p_gimnasio/rutina_form.html', {
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

    return render(request, 'p_gimnasio/rutina_form.html', {
        'form': form,
        'rutina': rutina,
        'titulo_pagina': 'Editar rutina',
        'boton': 'Guardar cambios',
    })


@login_required
def rutina_eliminar(request, pk):
    rutina = _rutina_del_entrenador_o_403(request, pk)

    if request.method != 'POST':
        return render(request, 'p_gimnasio/rutina_confirmar_eliminar.html', {
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
    return render(request, 'p_gimnasio/mis_registros.html', {
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

    return render(request, 'p_gimnasio/catalogo_form.html', {
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

    return render(request, 'p_gimnasio/catalogo_form.html', {
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
    contexto = {'rutina': rutina}
    if _es_socio(request.user) and rutina.entrenador_id != request.user.id:
        contexto['form_inscripcion'] = InscripcionForm()
        contexto['ya_inscripto'] = Inscripcion.objects.filter(
            rutina=rutina,
            socio=request.user,
        ).exists()
    return render(request, 'p_gimnasio/rutina_detalle.html', contexto)


@login_required
@require_POST
def inscripcion_crear(request, pk):
    if not _es_socio(request.user):
        raise PermissionDenied('Solo los socios pueden solicitar una inscripción.')

    rutina = get_object_or_404(Rutina, pk=pk)
    if rutina.entrenador_id == request.user.id:
        raise PermissionDenied('No puedes inscribirte en una rutina propia.')

    ya_inscripto = Inscripcion.objects.filter(
        rutina=rutina,
        socio=request.user,
    ).exists()
    if ya_inscripto:
        messages.warning(request, 'Ya tienes una solicitud para esta rutina.')
        return redirect('rutina_detalle', pk=rutina.pk)

    form = InscripcionForm(request.POST)
    if not form.is_valid():
        return render(request, 'p_gimnasio/rutina_detalle.html', {
            'rutina': rutina,
            'form_inscripcion': form,
            'ya_inscripto': False,
        }, status=400)

    inscripcion = form.save(commit=False)
    inscripcion.rutina = rutina
    inscripcion.socio = request.user
    try:
        with transaction.atomic():
            # Model.save() no ejecuta clean() automáticamente.
            inscripcion.full_clean()
            inscripcion.save()
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)
        return redirect('rutina_detalle', pk=rutina.pk)
    except IntegrityError:
        # Protege también ante dos envíos simultáneos y la restricción única.
        messages.warning(request, 'Ya tienes una solicitud para esta rutina.')
        return redirect('rutina_detalle', pk=rutina.pk)

    messages.success(request, 'Tu solicitud se envió al entrenador.')
    return redirect('mis_solicitudes')


@login_required
def mis_solicitudes(request):
    if not _es_socio(request.user):
        raise PermissionDenied('Solo los socios pueden ver sus solicitudes.')

    solicitudes = (
        Inscripcion.objects.filter(socio=request.user)
        .select_related('rutina', 'rutina__entrenador', 'rutina__disciplina')
        .prefetch_related('rutina__equipamientos')
    )
    return render(request, 'p_gimnasio/mis_solicitudes.html', {
        'solicitudes': solicitudes,
    })


@login_required
@require_POST
def inscripcion_cancelar(request, pk):
    if not _es_socio(request.user):
        raise PermissionDenied('Solo los socios pueden cancelar sus solicitudes.')

    inscripcion = get_object_or_404(Inscripcion, pk=pk, socio=request.user)
    if inscripcion.estado != 'pendiente':
        messages.error(
            request,
            'Solo puedes cancelar solicitudes que siguen pendientes.',
        )
    else:
        inscripcion.delete()
        messages.success(request, 'La solicitud pendiente fue cancelada.')
    return redirect('mis_solicitudes')


@login_required
def solicitudes_recibidas(request):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores pueden ver solicitudes recibidas.')

    solicitudes = (
        Inscripcion.objects.filter(rutina__entrenador=request.user)
        .select_related('socio', 'rutina', 'rutina__disciplina')
        .order_by('-fecha_creacion', '-id')
    )
    return render(request, 'p_gimnasio/solicitudes_recibidas.html', {
        'solicitudes': solicitudes,
    })


@login_required
@require_POST
def inscripcion_actualizar_estado(request, pk):
    if not _es_entrenador(request.user):
        raise PermissionDenied('Solo los entrenadores pueden responder solicitudes.')

    # El filtro por propietario evita que un entrenador responda solicitudes ajenas.
    inscripcion = get_object_or_404(
        Inscripcion,
        pk=pk,
        rutina__entrenador=request.user,
    )
    nuevo_estado = request.POST.get('estado')
    estados_permitidos = {'confirmada', 'rechazada'}
    if nuevo_estado not in estados_permitidos:
        messages.error(request, 'Selecciona confirmar o rechazar la solicitud.')
    else:
        inscripcion.estado = nuevo_estado
        inscripcion.save(update_fields=['estado'])
        etiqueta = inscripcion.get_estado_display().lower()
        messages.success(request, f'La solicitud quedó {etiqueta}.')
    return redirect('solicitudes_recibidas')
