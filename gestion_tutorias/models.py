from django.db import models
from django.contrib.auth.models import AbstractUser

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
    )
    descripcion = models.TextField(blank=True, null=True)
    calificacion_promedio = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return f"{self.username} ({self.rol})"



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
