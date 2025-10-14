from rest_framework import viewsets
from ..models import Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva
from ..serializers import (
    UsuarioSerializer, CategoriaSerializer, CursoSerializer,
    TutoriaSerializer, ReseñaSerializer, PagoSerializer, ReservaSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

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
