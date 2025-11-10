from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models_messaging import Conversacion, Mensaje
from .models import (
    Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva,
    DisponibilidadSemanal, BloqueoHorario, SolicitudReserva,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = (
        'id', 'username', 'email', 'descripcion', 'rol', 'especialidad', 'telefono',
        'zona_horaria', 'duracion_sesion_minutos', 'is_active', 'is_staff'
    )
    search_fields = ('username', 'email', 'rol')
    list_filter = ('rol', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'telefono', 'especialidad',
                'rol', 'calificacion_promedio', 'zona_horaria', 'duracion_sesion_minutos'
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
    list_display = ('id_curso', 'nombre', 'tutor','modalidad', 'categoria')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'tutor')


@admin.register(Reseña)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('id_reseña', 'puntuacion', 'fecha_reseña')
    search_fields = ('comentario',)
    list_filter = ('fecha_reseña',)


@admin.register(Tutoria)
class TutoriaAdmin(admin.ModelAdmin):
    list_display = ('id_tutoria', 'curso', 'fecha_tutoria','modalidad_tutoria', 'duracion', 'estado')
    list_filter = ('estado', 'curso')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'monto', 'metodo', 'fecha_pago', 'estado')
    list_filter = ('estado', 'metodo')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha_reserva', 'estado_reserva', 'estudiante', 'tutoria')
    list_filter = ('estado_reserva', 'fecha_reserva')


@admin.register(DisponibilidadSemanal)
class DisponibilidadSemanalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('usuario', 'dia_semana', 'activo')
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(BloqueoHorario)
class BloqueoHorarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'inicio', 'fin', 'motivo')
    list_filter = ('usuario',)
    search_fields = ('usuario__username', 'usuario__email', 'motivo')


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor', 'estudiante', 'curso', 'estado_solicitud', 'unread_tutor', 'unread_estudiante', 'created_at', 'updated_at')
    list_filter = ('estado_solicitud', 'tutor')
    search_fields = ('tutor__username', 'tutor__email', 'estudiante__username', 'estudiante__email')


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversacion', 'remitente', 'preview', 'creado_en', 'leido')
    list_filter = ('leido', 'remitente')
    search_fields = ('remitente__username', 'remitente__email', 'contenido')

    def preview(self, obj):
        return (obj.contenido or '')[:40]


@admin.register(SolicitudReserva)
class SolicitudReservaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'estudiante', 'curso', 'get_tutor', 'fecha_propuesta',
        'modalidad', 'duracion', 'estado', 'tutoria', 'reserva', 'creado_en'
    )
    list_filter = ('estado', 'modalidad', 'curso__tutor')
    search_fields = (
        'estudiante__username', 'estudiante__email', 'curso__nombre', 'curso__tutor__username', 'curso__tutor__email'
    )

    def get_tutor(self, obj):
        return getattr(obj.curso, 'tutor', None)
    get_tutor.short_description = 'Tutor'
