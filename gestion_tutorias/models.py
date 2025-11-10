from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

class Usuario(AbstractUser):
    
    email = models.EmailField(unique=True)  
    telefono = models.CharField(max_length=255, blank=True, null=True)
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    rol = models.CharField(
        max_length=50,
        choices=[
            ('tutor', 'Tutor'),
            ('estudiante', 'Estudiante'),
            ('admin', 'Administrador'),
        ],
        default='estudiante',  # Rol por defecto
    )
    descripcion = models.TextField(blank=True, null=True)
    calificacion_promedio = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    zona_horaria = models.CharField(max_length=50, default='America/Mexico_City')
    duracion_sesion_minutos = models.PositiveSmallIntegerField(default=60)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return f"{self.username} ({self.rol})"


WEEKDAYS = [
    (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
    (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
]


class DisponibilidadSemanal(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='disponibilidades_semanales'
    )
    dia_semana = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['usuario', 'dia_semana', 'hora_inicio']

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser menor a la de fin.')
        # Evitar solapamientos para el mismo usuario/día
        solapado = (
            DisponibilidadSemanal.objects
            .filter(usuario=self.usuario, dia_semana=self.dia_semana, activo=True)
            .exclude(pk=self.pk)
            .filter(hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio)
            .exists()
        )
        if solapado:
            raise ValidationError('Este bloque se superpone con otra disponibilidad existente.')

    def __str__(self):
        return f"{self.usuario.username} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class BloqueoHorario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='bloqueos')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['inicio']

    def clean(self):
        if self.inicio >= self.fin:
            raise ValidationError('La fecha/hora de inicio debe ser menor a la de fin.')

    def __str__(self):
        return f"Bloqueo {self.usuario.username} {self.inicio} - {self.fin}"



class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    modalidad = models.CharField(
        max_length=50,
        choices=[
            ('presencial', 'Presencial'),
            ('virtual', 'Virtual'),
            ('ambas', 'Ambas'),
        ],
    )
    ciudad = models.CharField(max_length=255, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tutor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cursos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='cursos')

    def __str__(self):
        return self.nombre


class Reseña(models.Model):
    id_reseña = models.AutoField(primary_key=True)
    comentario = models.TextField(blank=True, null=True)
    puntuacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_reseña = models.DateField()

    def __str__(self):
        return f"Reseña {self.id_reseña} - {self.puntuacion}"


class Tutoria(models.Model):
    id_tutoria = models.AutoField(primary_key=True)
    duracion = models.IntegerField(blank=True, null=True)
    fecha_tutoria = models.DateField()
    estado = models.BooleanField(default=True)
    modalidad_tutoria = models.CharField(
        max_length=50,
        choices=[
            ('presencial', 'Presencial'),
            ('virtual', 'Virtual'),
        ],
    )
    reseña = models.ForeignKey(Reseña, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutorias')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='tutorias')

    def __str__(self):
        return f"Tutoria {self.id_tutoria} - {self.curso.nombre}"


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=255)
    fecha_pago = models.DateField()
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"Pago {self.id_pago} - {self.monto}"


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha_reserva = models.DateField()
    estado_reserva = models.BooleanField(default=True)
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')
    tutoria = models.ForeignKey(Tutoria, on_delete=models.CASCADE, related_name='reservas')

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.estudiante.username}"


class SolicitudReserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]

    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_reserva',
        limit_choices_to={'rol': 'estudiante'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='solicitudes_reserva')
    fecha_propuesta = models.DateField()
    modalidad = models.CharField(
        max_length=50,
        choices=[('presencial', 'Presencial'), ('virtual', 'Virtual')]
    )
    duracion = models.PositiveSmallIntegerField(blank=True, null=True)
    mensaje = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    # Enlazamos la solicitud con los objetos creados al aceptar
    tutoria = models.ForeignKey(
        Tutoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes'
    )
    reserva = models.ForeignKey(
        Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes'
    )

    class Meta:
        ordering = ['-creado_en']
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'curso', 'fecha_propuesta'],
                condition=Q(estado='pendiente'),
                name='uniq_solicitud_pendiente_por_fecha'
            )
        ]

    def clean(self):
        if not self.curso or not self.curso.tutor_id:
            raise ValidationError('El curso debe tener un tutor asignado.')
        if self.estudiante and getattr(self.estudiante, 'rol', None) != 'estudiante':
            raise ValidationError('Solo usuarios con rol estudiante pueden crear solicitudes.')
        # Validación de modalidad respecto al curso
        if self.curso and self.curso.modalidad != 'ambas' and self.modalidad != self.curso.modalidad:
            raise ValidationError('La modalidad solicitada no coincide con la modalidad del curso.')
        # No permitir días pasados
        if self.fecha_propuesta and self.fecha_propuesta < timezone.now().date():
            raise ValidationError('La fecha propuesta no puede ser en el pasado.')

    def __str__(self):
        return f"Solicitud {self.id} - {self.estudiante.username} -> {self.curso.nombre} ({self.estado})"
