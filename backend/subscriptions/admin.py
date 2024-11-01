# subscriptions/admin.py
from django.contrib import admin
from .models import PlanSuscripcion, Suscripcion, Pago

@admin.register(PlanSuscripcion)
class PlanSuscripcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_dias', 'clases_disponibles', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('precio',)

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plan', 'fecha_inicio', 'fecha_fin', 'estado', 'clases_restantes')
    list_filter = ('estado', 'plan')
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('usuario', 'plan')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'suscripcion', 'monto', 'fecha_pago', 'estado', 'metodo_pago')
    list_filter = ('estado', 'metodo_pago')
    search_fields = ('suscripcion__usuario__username', 'referencia_pago')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('suscripcion', 'suscripcion__usuario')