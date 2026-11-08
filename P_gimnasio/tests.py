from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Inscripcion, Rutina


Usuario = get_user_model()


class InscripcionesTests(TestCase):
    def crear_usuario(self, username, rol):
        return Usuario.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='Prueba_segura_2026',
            rol=rol,
        )

    def setUp(self):
        self.socio = self.crear_usuario('socio1', Usuario.Rol.SOCIO)
        self.otro_socio = self.crear_usuario('socio2', Usuario.Rol.SOCIO)
        self.entrenador = self.crear_usuario('entrenador1', Usuario.Rol.ENTRENADOR)
        self.otro_entrenador = self.crear_usuario(
            'entrenador2', Usuario.Rol.ENTRENADOR
        )
        self.rutina = Rutina.objects.create(
            titulo='Rutina de fuerza',
            descripcion='Entrenamiento de fuerza general.',
            duracion=45,
            cupos=10,
            nivel='basico',
            entrenador=self.entrenador,
        )
        self.rutina_ajena = Rutina.objects.create(
            titulo='Movilidad matinal',
            descripcion='Ejercicios suaves de movilidad.',
            duracion=30,
            cupos=8,
            nivel='basico',
            entrenador=self.otro_entrenador,
        )

    def test_socio_crea_solicitud_sobre_rutina_ajena(self):
        self.client.force_login(self.socio)
        response = self.client.post(
            reverse('inscripcion_crear', args=[self.rutina.pk]),
            {'comentario': 'Me interesa participar.'},
        )

        self.assertRedirects(response, reverse('mis_solicitudes'))
        solicitud = Inscripcion.objects.get(rutina=self.rutina, socio=self.socio)
        self.assertEqual(solicitud.estado, 'pendiente')
        self.assertEqual(solicitud.comentario, 'Me interesa participar.')

    def test_socio_no_puede_duplicar_solicitud(self):
        Inscripcion.objects.create(rutina=self.rutina, socio=self.socio)
        self.client.force_login(self.socio)

        response = self.client.post(
            reverse('inscripcion_crear', args=[self.rutina.pk]),
            {'comentario': 'Segundo intento.'},
        )

        self.assertRedirects(
            response,
            reverse('rutina_detalle', args=[self.rutina.pk]),
        )
        self.assertEqual(
            Inscripcion.objects.filter(rutina=self.rutina, socio=self.socio).count(),
            1,
        )

    def test_mis_solicitudes_solo_muestra_las_del_socio(self):
        Inscripcion.objects.create(rutina=self.rutina, socio=self.socio)
        Inscripcion.objects.create(rutina=self.rutina_ajena, socio=self.otro_socio)
        self.client.force_login(self.socio)

        response = self.client.get(reverse('mis_solicitudes'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rutina.titulo)
        self.assertNotContains(response, self.rutina_ajena.titulo)

    def test_socio_puede_cancelar_solo_su_solicitud_pendiente(self):
        solicitud = Inscripcion.objects.create(rutina=self.rutina, socio=self.socio)
        self.client.force_login(self.socio)

        response = self.client.post(
            reverse('inscripcion_cancelar', args=[solicitud.pk])
        )

        self.assertRedirects(response, reverse('mis_solicitudes'))
        self.assertFalse(Inscripcion.objects.filter(pk=solicitud.pk).exists())

    def test_socio_no_puede_cancelar_solicitud_ya_resuelta(self):
        solicitud = Inscripcion.objects.create(
            rutina=self.rutina,
            socio=self.socio,
            estado='confirmada',
        )
        self.client.force_login(self.socio)

        self.client.post(reverse('inscripcion_cancelar', args=[solicitud.pk]))

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'confirmada')

    def test_entrenador_dueno_puede_confirmar_solicitud_recibida(self):
        solicitud = Inscripcion.objects.create(rutina=self.rutina, socio=self.socio)
        self.client.force_login(self.entrenador)

        response = self.client.post(
            reverse('inscripcion_actualizar_estado', args=[solicitud.pk]),
            {'estado': 'confirmada'},
        )

        self.assertRedirects(response, reverse('solicitudes_recibidas'))
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'confirmada')

    def test_entrenador_no_puede_modificar_solicitud_de_otro_entrenador(self):
        solicitud = Inscripcion.objects.create(
            rutina=self.rutina_ajena,
            socio=self.socio,
        )
        self.client.force_login(self.entrenador)

        response = self.client.post(
            reverse('inscripcion_actualizar_estado', args=[solicitud.pk]),
            {'estado': 'rechazada'},
        )

        self.assertEqual(response.status_code, 404)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'pendiente')

    def test_detalle_publico_se_renderiza_y_ofrece_login(self):
        response = self.client.get(
            reverse('rutina_detalle', args=[self.rutina.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inicia sesión como socio')

    def test_detalle_de_rutina_ofrece_formulario_al_socio(self):
        self.client.force_login(self.socio)
        response = self.client.get(
            reverse('rutina_detalle', args=[self.rutina.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enviar solicitud')

    def test_bandeja_del_entrenador_se_renderiza(self):
        Inscripcion.objects.create(rutina=self.rutina, socio=self.socio)
        self.client.force_login(self.entrenador)
        response = self.client.get(reverse('solicitudes_recibidas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmar')
        self.assertContains(response, 'Rechazar')

    def test_socio_no_puede_abrir_solicitudes_recibidas(self):
        self.client.force_login(self.socio)
        response = self.client.get(reverse('solicitudes_recibidas'))
        self.assertEqual(response.status_code, 403)
