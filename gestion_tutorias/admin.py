from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('id', 'username', 'email', 'rol', 'especialidad', 'telefono', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'rol')
    list_filter = ('rol', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'telefono', 'especialidad',
                'rol', 'calificacion_promedio'
            )
        }),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre')
    search_fields = ('nombre',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id_curso', 'nombre', 'tutor', 'categoria')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'tutor')


@admin.register(Reseña)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('id_reseña', 'puntuacion', 'fecha_reseña')
    search_fields = ('comentario',)
    list_filter = ('fecha_reseña',)


@admin.register(Tutoria)
class TutoriaAdmin(admin.ModelAdmin):
    list_display = ('id_tutoria', 'curso', 'fecha_tutoria', 'duracion', 'estado')
    list_filter = ('estado', 'curso')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'monto', 'metodo', 'fecha_pago', 'estado')
    list_filter = ('estado', 'metodo')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha_reserva', 'estado_reserva', 'estudiante', 'tutoria')
    list_filter = ('estado_reserva', 'fecha_reserva')
