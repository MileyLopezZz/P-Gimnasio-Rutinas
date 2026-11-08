from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.inicio_usuario, name='inicio_usuario'),
    path('rutinas/nueva/', views.rutina_crear, name='rutina_crear'),
    path('rutinas/<int:pk>/', views.rutina_detalle, name='rutina_detalle'),
    path(
        'rutinas/<int:pk>/inscribirse/',
        views.inscripcion_crear,
        name='inscripcion_crear',
    ),
    path('rutinas/<int:pk>/editar/', views.rutina_editar, name='rutina_editar'),
    path(
        'rutinas/<int:pk>/eliminar/',
        views.rutina_eliminar,
        name='rutina_eliminar',
    ),
    path('mis-registros/', views.mis_registros, name='mis_registros'),
    path('solicitudes/mias/', views.mis_solicitudes, name='mis_solicitudes'),
    path(
        'solicitudes/recibidas/',
        views.solicitudes_recibidas,
        name='solicitudes_recibidas',
    ),
    path(
        'solicitudes/<int:pk>/cancelar/',
        views.inscripcion_cancelar,
        name='inscripcion_cancelar',
    ),
    path(
        'solicitudes/<int:pk>/estado/',
        views.inscripcion_actualizar_estado,
        name='inscripcion_actualizar_estado',
    ),
    path('disciplinas/nueva/', views.disciplina_crear, name='disciplina_crear'),
    path(
        'equipamientos/nuevo/',
        views.equipamiento_crear,
        name='equipamiento_crear',
    ),
]
