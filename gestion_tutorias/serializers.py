from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from .models import (
    Usuario, Categoria, Curso, Tutoria, Reseña, Pago, Reserva,
    DisponibilidadSemanal, BloqueoHorario, SolicitudReserva
)
from .models_messaging import (Conversacion, Mensaje,)

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Notice we authenticate with `username=email`
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id, # type: ignore[attr-defined]
                "username": user.username,
                "email": user.email,
            },
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "rol", "descripcion", "telefono", "is_staff", "is_active"]
        read_only_fields = ["id", "username", "email", "rol", "descripcion", "telefono", "is_staff", "is_active"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id_categoria", "nombre", "descripcion"]

class CursoSerializer(serializers.ModelSerializer):
    # El tutor lo setea el servidor, solo lectura
    tutor = serializers.PrimaryKeyRelatedField(read_only=True)
    # Enviamos el id de la categoría desde el FE
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )

    class Meta:
        model = Curso
        fields = [
            "id_curso", "nombre", "descripcion", "modalidad",
            "ciudad", "precio", "tutor", "categoria"
        ]

class ReseñaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = '__all__'

class TutoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutoria
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'


class SolicitudReservaSerializer(serializers.ModelSerializer):
    tutor = serializers.SerializerMethodField(read_only=True)
    tutoria = serializers.PrimaryKeyRelatedField(read_only=True)
    reserva = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SolicitudReserva
        fields = [
            'id', 'estudiante', 'curso', 'tutor', 'fecha_propuesta',
            'modalidad', 'duracion', 'mensaje', 'estado',
            'creado_en', 'actualizado_en', 'tutoria', 'reserva'
        ]
        read_only_fields = ['id', 'estudiante', 'tutor', 'estado', 'creado_en', 'actualizado_en', 'tutoria', 'reserva']

    def get_tutor(self, obj):
        return getattr(getattr(obj, 'curso', None), 'tutor_id', None)

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        curso = attrs.get('curso')
        fecha = attrs.get('fecha_propuesta')
        modalidad = attrs.get('modalidad')

        # Rol y curso válidos
        if not user or getattr(user, 'rol', None) != 'estudiante':
            raise serializers.ValidationError('Solo estudiantes pueden crear solicitudes.')
        if not curso or not getattr(curso, 'tutor_id', None):
            raise serializers.ValidationError('El curso debe existir y tener un tutor.')

        # Modalidad respecto al curso
        if curso.modalidad != 'ambas' and modalidad != curso.modalidad:
            raise serializers.ValidationError('La modalidad solicitada no coincide con la del curso.')

        # Fecha futura
        from django.utils import timezone
        if fecha and fecha < timezone.now().date():
            raise serializers.ValidationError('La fecha propuesta no puede ser en el pasado.')

        # Duplicado pendiente
        if fecha and curso:
            exists = SolicitudReserva.objects.filter(
                estudiante=user, curso=curso, fecha_propuesta=fecha, estado='pendiente'
            ).exists()
            if exists:
                raise serializers.ValidationError('Ya existe una solicitud pendiente para ese curso y fecha.')

        return attrs


class DisponibilidadSemanalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadSemanal
        fields = '__all__'
        read_only_fields = ['usuario']


class BloqueoHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloqueoHorario
        fields = '__all__'
        read_only_fields = ['usuario']


class ConversacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversacion
        fields = '__all__'


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = '__all__'
        read_only_fields = ['remitente']


class MensajeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ('id', 'remitente', 'contenido', 'creado_en', 'leido')


class ConversacionListItemSerializer(serializers.ModelSerializer):
    ultimo_mensaje = serializers.SerializerMethodField()
    no_leidos = serializers.SerializerMethodField()

    class Meta:
        model = Conversacion
        fields = (
            'id', 'tutor', 'estudiante', 'curso', 'estado_solicitud',
            'unread_tutor', 'unread_estudiante', 'updated_at', 'ultimo_mensaje',
            'no_leidos'
        )

    def get_ultimo_mensaje(self, obj):
        msg = obj.mensajes.order_by('-creado_en').first()
        if not msg:
            return None
        return MensajeSimpleSerializer(msg).data

    def get_no_leidos(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user:
            return 0
        return obj.unread_tutor if user == obj.tutor else obj.unread_estudiante
