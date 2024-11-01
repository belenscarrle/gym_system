from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'usuarios': request.build_absolute_uri('/api/usuarios/'),
        'autenticacion': {
            'obtener_token': reverse('token_obtain_pair', request=request),
            'refrescar_token': reverse('token_refresh', request=request),
        },
        'subscriptions': request.build_absolute_uri('/api/subscriptions/'),
        'admin': request.build_absolute_uri('/admin/'),
    })

urlpatterns = [
    # Vista raíz de la API
    path('', api_root, name='api-root'),
    
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # URLs de la API
    path('api/usuarios/', include('usuarios.urls')),
    
    # URLs para autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/subscriptions/', include('subscriptions.urls')),
]