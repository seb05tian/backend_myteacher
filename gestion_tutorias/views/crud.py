from rest_framework import viewsets
from ..models import Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva
from ..serializers import (UsuarioSerializer, CategoriaSerializer, CursoSerializer, TutoriaSerializer, ReseñaSerializer, PagoSerializer, ReservaSerializer)
from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

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
