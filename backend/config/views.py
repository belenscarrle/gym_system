# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request):
    return Response({
        'usuarios': reverse('usuarios-list', request=request),
        'token': reverse('token_obtain_pair', request=request),
        'subscriptions': reverse('subscriptions-list', request=request),
        # Agrega aquí todos tus endpoints
    })