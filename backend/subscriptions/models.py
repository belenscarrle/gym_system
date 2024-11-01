# subscriptions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class PlanSuscripcion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.IntegerField()
    clases_disponibles = models.IntegerField()
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    class Meta:
        verbose_name = "Plan de Suscripción"
        verbose_name_plural = "Planes de Suscripción"

class Suscripcion(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('PENDIENTE', 'Pendiente de Pago'),
        ('CANCELADA', 'Cancelada'),
        ('EXPIRADA', 'Expirada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        related_name='suscripciones'
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    clases_restantes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.plan.nombre}"

    def esta_activa(self):
        ahora = timezone.now()
        return (
            self.estado == 'ACTIVA' and
            self.fecha_inicio <= ahora <= self.fecha_fin and
            self.clases_restantes > 0
        )

    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]

    METODO_CHOICES = [
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('EFECTIVO', 'Efectivo'),
    ]

    suscripcion = models.ForeignKey(
        Suscripcion,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_CHOICES
    )
    referencia_pago = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago {self.id} - {self.suscripcion.usuario.username}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"