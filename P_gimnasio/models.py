from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# ==========================================================
# 1. USUARIO
# Guarda las cuentas de socios y entrenadores.
# ==========================================================
class Usuario(AbstractUser):

    # Roles que puede tener una cuenta.
    class Rol(models.TextChoices):
        SOCIO = 'socio', 'Socio'
        ENTRENADOR = 'entrenador', 'Entrenador'

    # El correo es obligatorio y no puede repetirse.
    email = models.EmailField(
        unique=True,
        verbose_name='Correo electronico',
    )

    # Las cuentas nuevas seran socios por defecto.
    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.SOCIO,
    )

    def __str__(self):
        return self.username


# ==========================================================
# 2. DISCIPLINA
# Catalogo de actividades: yoga, spinning, funcional, etc.
# ==========================================================
class Disciplina(models.Model):

    # Cada disciplina tendra un nombre unico.
    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        # Orden alfabetico por nombre.
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================================================
# 3. EQUIPAMIENTO
# Etiquetas de las rutinas: mancuernas, banco, etc.
# ==========================================================
class Equipamiento(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================================================
# 4. RUTINA
# Plan de ejercicios publicado por un entrenador.
# ==========================================================
class Rutina(models.Model):

    # El primer valor se guarda en la base.
    # El segundo es el texto que vera la persona.
    NIVELES = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    titulo = models.CharField(
        max_length=150,
    )

    # Permite escribir un texto extenso.
    descripcion = models.TextField()

    # La duracion debe estar entre 10 y 120 minutos.
    duracion = models.PositiveIntegerField(
        verbose_name='Duracion en minutos',
        validators=[
            MinValueValidator(10),
            MaxValueValidator(120),
        ],
    )

    # Los cupos deben estar entre 1 y 30.
    cupos = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30),
        ],
    )

    nivel = models.CharField(
        max_length=10,
        choices=NIVELES,
        default='basico',
    )

    # Guarda la fecha y hora automaticamente al crear la rutina.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    # Cada rutina pertenece a un entrenador.
    # Un entrenador puede publicar muchas rutinas.
    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # Si se elimina el entrenador, se eliminan sus rutinas.
        on_delete=models.CASCADE,

        # Permite consultar las rutinas desde el usuario.
        related_name='rutinas',

        # Limita las opciones de los formularios a entrenadores.
        limit_choices_to={'rol': 'entrenador'},
    )

    # La disciplina es opcional.
    disciplina = models.ForeignKey(
        Disciplina,

        # Si se elimina la disciplina, la rutina se conserva
        # y queda sin disciplina asignada.
        on_delete=models.SET_NULL,

        # Permite un valor vacio en la base de datos.
        null=True,

        # Permite dejar el campo vacio en los formularios.
        blank=True,

        related_name='rutinas',
    )

    # Relacion de muchos a muchos:
    # una rutina puede tener varios equipamientos y
    # un equipamiento puede estar en varias rutinas.
    #
    # ESTE CAMPO CREA AUTOMATICAMENTE LA SEXTA TABLA.
    equipamientos = models.ManyToManyField(
        Equipamiento,
        blank=True,
        related_name='rutinas',
    )

    class Meta:
        # Primero apareceran las rutinas mas recientes.
        ordering = ['-fecha_creacion', '-id']

    def clean(self):
        # Conserva la validacion del modelo de Django.
        super().clean()

        # Si se selecciono un usuario, revisamos su rol.
        if self.entrenador_id:
            es_entrenador = Usuario.objects.filter(
                pk=self.entrenador_id,
                rol=Usuario.Rol.ENTRENADOR,
            ).exists()

            # exists() devuelve True si encuentra una coincidencia.
            if not es_entrenador:
                raise ValidationError(
                    'La rutina debe pertenecer a un entrenador.'
                )

    def __str__(self):
        return self.titulo


# ==========================================================
# 5. INSCRIPCION
# Solicitud de un socio para participar en una rutina.
# ==========================================================
class Inscripcion(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('rechazada', 'Rechazada'),
    ]

    # Cada inscripcion corresponde a una rutina.
    rutina = models.ForeignKey(
        Rutina,

        # Si se elimina la rutina, se eliminan sus inscripciones.
        on_delete=models.CASCADE,

        related_name='inscripciones',
    )

    # Cada inscripcion pertenece a un socio.
    socio = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # Si se elimina el socio, se eliminan sus inscripciones.
        on_delete=models.CASCADE,

        related_name='inscripciones',

        # En los formularios se muestran usuarios con rol socio.
        limit_choices_to={'rol': 'socio'},
    )

    # El comentario es opcional.
    comentario = models.TextField(
        blank=True,
    )

    # Guarda automaticamente cuando se creo la inscripcion.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    # Una solicitud nueva siempre empieza pendiente.
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='pendiente',
    )

    class Meta:
        ordering = ['-fecha_creacion', '-id']
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'

        # Impide que el mismo socio se inscriba dos veces
        # en la misma rutina.
        # Esta restriccion tambien se crea en la base de datos.
        constraints = [
            models.UniqueConstraint(
                fields=['rutina', 'socio'],
                name='inscripcion_unica_por_socio_y_rutina',
            ),
        ]

    def clean(self):
        super().clean()

        # Comprobamos la relacion cuando ambos campos tienen valor.
        if self.rutina_id and self.socio_id:

            # Busca si quien se inscribe tambien es el duenio.
            es_rutina_propia = Rutina.objects.filter(
                pk=self.rutina_id,
                entrenador_id=self.socio_id,
            ).exists()

            if es_rutina_propia:
                raise ValidationError(
                    'No puedes inscribirte en una rutina propia.'
                )

        # Comprobamos que el usuario tenga el rol socio.
        if self.socio_id:
            es_socio = Usuario.objects.filter(
                pk=self.socio_id,
                rol=Usuario.Rol.SOCIO,
            ).exists()

            if not es_socio:
                raise ValidationError(
                    'Solo los usuarios con rol socio pueden inscribirse.'
                )

    def __str__(self):
        # Muestra quien se inscribio y en que rutina.
        return f'{self.socio} - {self.rutina}'