from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import IngresoForm


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('rutinas/', views.lista_rutinas, name='lista_rutinas'),
    path('registro/', views.registro, name='registro'),
    path('rutinas/<int:pk>/',views.detalle_rutina,name='detalle_rutina'),

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