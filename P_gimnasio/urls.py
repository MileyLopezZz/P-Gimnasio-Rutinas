from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import IngresoForm


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('rutinas/', views.lista_rutinas, name='lista_rutinas'),
    path('registro/', views.registro, name='registro'),
    path('rutinas/<int:pk>/detalle/',views.detalle_rutina,name='detalle_rutina'),

    path(
        'login/',auth_views.LoginView.as_view(
            template_name='login.html',
            authentication_form=IngresoForm,
            redirect_authenticated_user=True,
        ),name='login'),
    
    path('logout/',auth_views.LogoutView.as_view(next_page='inicio'),name='logout'),
    path('cuenta/',views.cuenta,name='cuenta'),
    path('cuenta/editar/',views.editar_perfil,name='editar_perfil'),

    path('cuenta/password/',auth_views.PasswordChangeView.as_view(
            template_name='cambiar_password.html',
            success_url=reverse_lazy('cuenta'),
        ),name='cambiar_password'),
]


urlpatterns += [
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
