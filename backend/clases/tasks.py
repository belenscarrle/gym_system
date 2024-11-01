from celery import shared_task
from django.utils import timezone
from .models import ListaEspera

@shared_task
def verificar_expiraciones_lista_espera():
    """
    Tarea programada para verificar y gestionar expiración de promociones
    """
    # Obtener todas las promociones pendientes de expirar
    promociones_expirar = ListaEspera.objects.filter(
        estado='promocionado',
        fecha_expiracion__lt=timezone.now()
    )

    for promocion in promociones_expirar:
        promocion.verificar_expiracion()

@shared_task
def limpiar_listas_espera_antiguas():
    """
    Elimina listas de espera antiguas para mantener la base de datos limpia
    """
    fecha_limite = timezone.now() - timezone.timedelta(days=30)
    
    # Eliminar registros de lista de espera con más de 30 días
    ListaEspera.objects.filter(
        fecha_registro__lt=fecha_limite
    ).delete()