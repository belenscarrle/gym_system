# subscriptions/serializers.py
from rest_framework import serializers
from .models import PlanSuscripcion, Suscripcion, Pago

class PlanSuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanSuscripcion
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'duracion_dias', 'clases_disponibles', 'activo'
        ]

class SuscripcionSerializer(serializers.ModelSerializer):
    plan_nombre = serializers.CharField(source='plan.nombre', read_only=True)
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name',
        read_only=True
    )

    class Meta:
        model = Suscripcion
        fields = [
            'id', 'usuario', 'plan', 'plan_nombre', 'usuario_nombre',
            'fecha_inicio', 'fecha_fin', 'estado', 'clases_restantes'
        ]
        read_only_fields = [
            'fecha_inicio', 'fecha_fin', 'estado', 'clases_restantes'
        ]

class CrearSuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = ['plan']

    def validate_plan(self, value):
        if not value.activo:
            raise serializers.ValidationError(
                "Este plan no está disponible actualmente."
            )
        return value

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            'id', 'suscripcion', 'monto', 'fecha_pago',
            'estado', 'metodo_pago', 'referencia_pago'
        ]
        read_only_fields = ['fecha_pago', 'estado']