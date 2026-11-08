from django.urls import path

from . import views

urlpatterns = [
    path('rutinas/nueva/', views.rutina_crear, name='rutina_crear'),
    path('rutinas/<int:pk>/', views.rutina_detalle, name='rutina_detalle'),
    path('rutinas/<int:pk>/editar/', views.rutina_editar, name='rutina_editar'),
    path(
        'rutinas/<int:pk>/eliminar/',
        views.rutina_eliminar,
        name='rutina_eliminar',
    ),
    path('mis-registros/', views.mis_registros, name='mis_registros'),
    path('disciplinas/nueva/', views.disciplina_crear, name='disciplina_crear'),
    path(
        'equipamientos/nuevo/',
        views.equipamiento_crear,
        name='equipamiento_crear',
    ),
]