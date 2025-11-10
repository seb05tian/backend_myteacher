from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views.users import LoginView, RegisterView, MeView  
from .views.reviews import crear_resena, resenas_recibidas, resenas_enviadas
from rest_framework.routers import DefaultRouter
from .views.crud import (
    UsuarioViewSet, CategoriaViewSet, CursoViewSet,
    TutoriaViewSet, ReseñaViewSet, PagoViewSet, ReservaViewSet,
    DisponibilidadSemanalViewSet, BloqueoHorarioViewSet,
    ConversacionViewSet, MensajeViewSet,
    SolicitudReservaViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'tutorias', TutoriaViewSet)
router.register(r'reseñas', ReseñaViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'reservas', ReservaViewSet)
router.register(r'solicitudes-reserva', SolicitudReservaViewSet, basename='solicitud-reserva')
router.register(r'disponibilidades', DisponibilidadSemanalViewSet, basename='disponibilidad')
router.register(r'bloqueos', BloqueoHorarioViewSet, basename='bloqueo')
router.register(r'conversaciones', ConversacionViewSet, basename='conversacion')
router.register(r'mensajes', MensajeViewSet, basename='mensaje')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    # Reseñas: create y listados útiles para el front
    path('resenas/crear/', crear_resena, name='crear_resena'),
    path('resenas/recibidas/', resenas_recibidas, name='resenas_recibidas'),
    path('resenas/enviadas/', resenas_enviadas, name='resenas_enviadas'),
    # JWT obtain/refresh endpoints compatibles con el FE
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Alias comunes por compatibilidad
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('crud/', include(router.urls)),
]


