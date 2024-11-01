# usuarios/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioUpdateSerializer,
    CambioPasswordSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de usuarios.
    
    list: GET /api/usuarios/
    create: POST /api/usuarios/
    retrieve: GET /api/usuarios/{id}/
    update: PUT /api/usuarios/{id}/
    partial_update: PATCH /api/usuarios/{id}/
    destroy: DELETE /api/usuarios/{id}/
    """
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """
        Establece los permisos según la acción:
        - Registro: permitir a todos
        - Otras acciones: solo usuarios autenticados
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo usuario.
        POST /api/usuarios/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                UsuarioSerializer(usuario).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna la información del usuario actual.
        GET /api/usuarios/me/
        """
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """
        Cambia la contraseña del usuario.
        POST /api/usuarios/{id}/cambiar_password/
        """
        usuario = self.get_object()
        serializer = CambioPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not usuario.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Contraseña actual incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            usuario.set_password(serializer.validated_data['new_password'])
            usuario.save()
            return Response({'mensaje': 'Contraseña actualizada correctamente'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)