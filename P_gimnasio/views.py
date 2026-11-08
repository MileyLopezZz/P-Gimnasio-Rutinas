from django.shortcuts import render, get_object_or_404,redirect
from .models import Rutina,Disciplina,Inscripcion
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .forms import RegistroForm, PerfilForm
from django.contrib.auth.decorators import login_required

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