from rest_framework import viewsets
from ..models import (
    Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva,
    DisponibilidadSemanal, BloqueoHorario, SolicitudReserva,
)
from ..serializers import (
    UsuarioSerializer, CategoriaSerializer, CursoSerializer, TutoriaSerializer,
    ReseñaSerializer, PagoSerializer, ReservaSerializer,
    DisponibilidadSemanalSerializer, BloqueoHorarioSerializer,
    ConversacionSerializer, MensajeSerializer, SolicitudReservaSerializer, ConversacionListItemSerializer
)
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Avg
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..models_messaging import Conversacion, Mensaje
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
User = get_user_model()
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer



class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "descripcion"]

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.select_related("tutor", "categoria").all()
    serializer_class = CursoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "descripcion", "ciudad"]

    def get_queryset(self):
        qs = Curso.objects.select_related("tutor", "categoria").all()
        cat = self.request.query_params.get("categoria")
        if cat not in (None, "", "null"):
            qs = qs.filter(categoria_id=cat)
        return qs

    def perform_create(self, serializer):
        # El tutor es el usuario autenticado
        curso = serializer.save(tutor=self.request.user)
        # Si no era tutor, promoverlo
        user = self.request.user
        if getattr(user, "rol", None) != "tutor":
            user.rol = "tutor"
            
            user.save(update_fields=["rol"])
        return curso

class ReseñaViewSet(viewsets.ModelViewSet):
    queryset = Reseña.objects.all()
    serializer_class = ReseñaSerializer

class TutoriaViewSet(viewsets.ModelViewSet):
    queryset = Tutoria.objects.all()
    serializer_class = TutoriaSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer


class SolicitudReservaViewSet(viewsets.ModelViewSet):
    queryset = SolicitudReserva.objects.select_related('curso', 'curso__tutor', 'estudiante').all().order_by('-creado_en')
    serializer_class = SolicitudReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if getattr(user, 'is_staff', False):
            return qs
        if getattr(user, 'rol', None) == 'tutor':
            return qs.filter(curso__tutor=user)
        return qs.filter(estudiante=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'rol', None) != 'estudiante':
            raise PermissionDenied('Solo los estudiantes pueden crear solicitudes de reserva.')
        serializer.save(estudiante=user)

    @action(detail=True, methods=['post'], url_path='aceptar')
    def aceptar(self, request, pk=None):
        solicitud = self.get_object()
        user = request.user
        tutor_id = getattr(getattr(solicitud, 'curso', None), 'tutor_id', None)
        if not (getattr(user, 'is_staff', False) or user.id == tutor_id):
            raise PermissionDenied('Solo el tutor del curso puede aceptar la solicitud.')
        if solicitud.estado != 'pendiente':
            return Response({'detail': 'La solicitud no está en estado pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear Tutoria y Reserva automáticamente (ignorar pago)
        duracion_min = solicitud.duracion or getattr(solicitud.curso.tutor, 'duracion_sesion_minutos', 60)
        tutoria = Tutoria.objects.create(
            duracion=duracion_min,
            fecha_tutoria=solicitud.fecha_propuesta,
            estado=True,
            modalidad_tutoria=solicitud.modalidad,
            reseña=None,
            curso=solicitud.curso,
        )
        reserva = Reserva.objects.create(
            fecha_reserva=timezone.now().date(),
            estado_reserva=True,
            estudiante=solicitud.estudiante,
            pago=None,
            tutoria=tutoria,
        )

        solicitud.estado = 'aceptada'
        solicitud.tutoria = tutoria
        solicitud.reserva = reserva
        solicitud.save(update_fields=['estado', 'actualizado_en', 'tutoria', 'reserva'])

        return Response({
            'solicitud_id': solicitud.id,
            'estado_solicitud': solicitud.estado,
            'tutoria_id': tutoria.id_tutoria,
            'reserva_id': reserva.id_reserva,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        solicitud = self.get_object()
        user = request.user
        tutor_id = getattr(getattr(solicitud, 'curso', None), 'tutor_id', None)
        if not (getattr(user, 'is_staff', False) or user.id == tutor_id):
            raise PermissionDenied('Solo el tutor del curso puede rechazar la solicitud.')
        if solicitud.estado != 'pendiente':
            return Response({'detail': 'La solicitud no está en estado pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = 'rechazada'
        solicitud.save(update_fields=['estado', 'actualizado_en'])
        return Response({
            'solicitud_id': solicitud.id,
            'estado_solicitud': solicitud.estado,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        solicitud = self.get_object()
        user = request.user
        if not (getattr(user, 'is_staff', False) or user.id == getattr(solicitud.estudiante, 'id', None)):
            raise PermissionDenied('Solo el estudiante creador puede cancelar la solicitud.')
        if solicitud.estado != 'pendiente':
            return Response({'detail': 'Solo se pueden cancelar solicitudes en estado pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = 'cancelada'
        solicitud.save(update_fields=['estado', 'actualizado_en'])
        return Response({
            'solicitud_id': solicitud.id,
            'estado_solicitud': solicitud.estado,
        }, status=status.HTTP_200_OK)

class DisponibilidadSemanalViewSet(viewsets.ModelViewSet):
    serializer_class = DisponibilidadSemanalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = DisponibilidadSemanal.objects.all().order_by('dia_semana', 'hora_inicio')
        user = self.request.user
        if getattr(user, 'is_staff', False):
            return qs
        return qs.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class BloqueoHorarioViewSet(viewsets.ModelViewSet):
    serializer_class = BloqueoHorarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = BloqueoHorario.objects.all().order_by('-inicio')
        user = self.request.user
        if getattr(user, 'is_staff', False):
            return qs
        return qs.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ConversacionViewSet(viewsets.ModelViewSet):
    serializer_class = ConversacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Conversacion.objects.all().order_by('-updated_at')
        if getattr(user, 'is_staff', False):
            return qs
        return qs.filter(Q(tutor=user) | Q(estudiante=user))

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'rol', None) == 'estudiante':
            serializer.save(estudiante=user)
        elif getattr(user, 'rol', None) == 'tutor':
            serializer.save(tutor=user)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        convs = self.get_queryset()
        data = ConversacionListItemSerializer(convs, many=True, context={'request': request}).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        conv = self.get_object()
        if request.user != conv.tutor and not getattr(request.user, 'is_staff', False):
            return Response({'detail': 'Solo el tutor puede aceptar.'}, status=status.HTTP_403_FORBIDDEN)
        conv.estado_solicitud = 'aceptada'
        conv.save(update_fields=['estado_solicitud', 'updated_at'])
        return Response(ConversacionSerializer(conv).data)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        conv = self.get_object()
        if request.user != conv.tutor and not getattr(request.user, 'is_staff', False):
            return Response({'detail': 'Solo el tutor puede rechazar.'}, status=status.HTTP_403_FORBIDDEN)
        conv.estado_solicitud = 'rechazada'
        conv.save(update_fields=['estado_solicitud', 'updated_at'])
        return Response(ConversacionSerializer(conv).data)

    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        conv = self.get_object()
        if request.user not in (conv.tutor, conv.estudiante) and not getattr(request.user, 'is_staff', False):
            return Response({'detail': 'No puedes archivar esta conversación.'}, status=status.HTTP_403_FORBIDDEN)
        conv.estado_solicitud = 'archivada'
        conv.save(update_fields=['estado_solicitud', 'updated_at'])
        return Response(ConversacionSerializer(conv).data)

    @action(detail=True, methods=['post'])
    def marcar_leidos(self, request, pk=None):
        conv = self.get_object()
        if request.user not in (conv.tutor, conv.estudiante) and not getattr(request.user, 'is_staff', False):
            return Response({'detail': 'No puedes modificar esta conversación.'}, status=status.HTTP_403_FORBIDDEN)
        conv.marcar_leidos_por(request.user)
        return Response(ConversacionSerializer(conv).data)


class MensajeViewSet(viewsets.ModelViewSet):
    serializer_class = MensajeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Mensaje.objects.select_related('conversacion').all()
        if getattr(user, 'is_staff', False):
            base = qs
        else:
            base = qs.filter(Q(conversacion__tutor=user) | Q(conversacion__estudiante=user))
        conv_id = self.request.query_params.get('conversacion')
        if conv_id:
            base = base.filter(conversacion_id=conv_id)
        return base

    def perform_create(self, serializer):
        conversacion = serializer.validated_data.get('conversacion')
        if conversacion and self.request.user not in (conversacion.tutor, conversacion.estudiante) and not getattr(self.request.user, 'is_staff', False):
            raise PermissionDenied('No perteneces a esta conversación.')
        mensaje = serializer.save(remitente=self.request.user)
        # actualizar contadores de no leídos y timestamp de conversación
        conv = mensaje.conversacion
        if self.request.user == conv.tutor:
            conv.unread_estudiante = (conv.unread_estudiante or 0) + 1
        else:
            conv.unread_tutor = (conv.unread_tutor or 0) + 1
        conv.save(update_fields=['unread_tutor', 'unread_estudiante', 'updated_at'])

