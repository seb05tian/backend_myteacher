from django.urls import path, include
from .views.users import LoginView, RegisterView, MeView  
from rest_framework.routers import DefaultRouter
from .views.crud import (
    UsuarioViewSet, CategoriaViewSet, CursoViewSet,
    TutoriaViewSet, ReseñaViewSet, PagoViewSet, ReservaViewSet
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'tutorias', TutoriaViewSet)
router.register(r'reseñas', ReseñaViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('crud/', include(router.urls)),
]


