from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from django.apps import apps

from ..models import Reserva

# Obtener el modelo de Reseña evitando problemas con el caracter ñ
ResenaModel = apps.get_model('gestion_tutorias', 'Rese\u00f1a')

# Serializer simple y autocontenido para Reseña
from rest_framework import serializers


class ResenaSimpleSerializer(serializers.ModelSerializer):
    tutor_id = serializers.SerializerMethodField()
    estudiante_id = serializers.SerializerMethodField()
    tutoria_id = serializers.SerializerMethodField()
    class Meta:
        model = ResenaModel
        fields = '__all__'

    def get_tutoria_id(self, obj):
        t = getattr(obj, 'tutorias', None)
        if t is None:
            return None
        first = t.first()
        return getattr(first, 'id_tutoria', None) if first else None

    def get_tutor_id(self, obj):
        t = getattr(obj, 'tutorias', None)
        if not t:
            return None
        tut = t.first()
        if not tut:
            return None
        curso = getattr(tut, 'curso', None)
        return getattr(getattr(curso, 'tutor', None), 'id', None)

    def get_estudiante_id(self, obj):
        t = getattr(obj, 'tutorias', None)
        if not t:
            return None
        tut = t.first()
        if not tut:
            return None
        reserva = getattr(tut, 'reservas', None)
        if not reserva:
            return None
        r = reserva.first()
        return getattr(getattr(r, 'estudiante', None), 'id', None) if r else None


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def crear_resena(request):
    reserva_id = request.data.get('reserva')
    comentario = request.data.get('comentario', '')
    puntuacion = request.data.get('puntuacion')

    if not reserva_id:
        return Response({'detail': 'Falta el id de la reserva.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        reserva = Reserva.objects.select_related('tutoria__curso__tutor').get(pk=reserva_id)
    except Reserva.DoesNotExist:
        return Response({'detail': 'Reserva no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != getattr(reserva, 'estudiante', None) and not getattr(request.user, 'is_staff', False):
        return Response({'detail': 'No puedes calificar esta reserva.'}, status=status.HTTP_403_FORBIDDEN)

    tutoria = getattr(reserva, 'tutoria', None)
    if not tutoria:
        return Response({'detail': 'La reserva no tiene tutoría.'}, status=status.HTTP_400_BAD_REQUEST)

    # Ya tiene reseña?
    if getattr(tutoria, 'rese\u00f1a_id', None):
        return Response({'detail': 'La tutoría ya tiene una reseña.'}, status=status.HTTP_400_BAD_REQUEST)

    if tutoria.fecha_tutoria and tutoria.fecha_tutoria > timezone.now().date():
        return Response({'detail': 'Solo puedes calificar tutorías ya realizadas.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        val = float(puntuacion)
    except Exception:
        return Response({'detail': 'Puntuación inválida.'}, status=status.HTTP_400_BAD_REQUEST)
    if val < 0 or val > 5:
        return Response({'detail': 'La puntuación debe estar entre 0 y 5.'}, status=status.HTTP_400_BAD_REQUEST)

    # Crear reseña
    resena = ResenaModel.objects.create(
        comentario=comentario,
        puntuacion=val,
        fecha_reseña=timezone.now().date()
    )

    # Enlazar con la tutoría
    setattr(tutoria, 'rese\u00f1a', resena)
    tutoria.save(update_fields=['rese\u00f1a'])

    # Recalcular promedio del tutor
    tutor = tutoria.curso.tutor
    avg = (ResenaModel.objects
           .filter(tutorias__curso__tutor=tutor)
           .aggregate(a=Avg('puntuacion'))['a'])
    tutor.calificacion_promedio = avg or 0
    tutor.save(update_fields=['calificacion_promedio'])

    return Response(ResenaSimpleSerializer(resena).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def resenas_recibidas(request):
    user = request.user
    if getattr(user, 'rol', None) != 'tutor' and not getattr(user, 'is_staff', False):
        return Response({'detail': 'Solo tutores o staff.'}, status=status.HTTP_403_FORBIDDEN)
    qs = ResenaModel.objects.filter(tutorias__curso__tutor=user).distinct()
    return Response(ResenaSimpleSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def resenas_enviadas(request):
    user = request.user
    if getattr(user, 'rol', None) != 'estudiante' and not getattr(user, 'is_staff', False):
        return Response({'detail': 'Solo estudiantes o staff.'}, status=status.HTTP_403_FORBIDDEN)
    qs = ResenaModel.objects.filter(tutorias__reservas__estudiante=user).distinct()
    return Response(ResenaSimpleSerializer(qs, many=True).data)
