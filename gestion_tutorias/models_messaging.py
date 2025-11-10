from django.db import models
from django.core.exceptions import ValidationError


class Conversacion(models.Model):
    tutor = models.ForeignKey(
        'gestion_tutorias.Usuario',
        on_delete=models.CASCADE,
        related_name='conversaciones_como_tutor',
        limit_choices_to={'rol': 'tutor'}
    )
    estudiante = models.ForeignKey(
        'gestion_tutorias.Usuario',
        on_delete=models.CASCADE,
        related_name='conversaciones_como_estudiante',
        limit_choices_to={'rol': 'estudiante'}
    )
    curso = models.ForeignKey('gestion_tutorias.Curso', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversaciones')
    estado_solicitud = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada'), ('archivada', 'Archivada')],
        default='pendiente'
    )
    # Contadores de no leídos por participante
    unread_tutor = models.PositiveIntegerField(default=0)
    unread_estudiante = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conv {self.id}"

    def marcar_leidos_por(self, user):
        if user_id := getattr(user, 'id', None):
            if user_id == self.tutor_id and self.unread_tutor:
                self.unread_tutor = 0
                self.save(update_fields=['unread_tutor'])
            elif user_id == self.estudiante_id and self.unread_estudiante:
                self.unread_estudiante = 0
                self.save(update_fields=['unread_estudiante'])


class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey('gestion_tutorias.Usuario', on_delete=models.CASCADE, related_name='mensajes_enviados')
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['creado_en']

    def clean(self):
        if self.conversacion_id and self.remitente_id:
            if self.remitente_id not in (self.conversacion.tutor_id, self.conversacion.estudiante_id):
                raise ValidationError('El remitente no pertenece a la conversación.')

    def __str__(self):
        return f"Msg {self.id} conv:{self.conversacion_id}"
