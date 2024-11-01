# clases/serializers.py
from rest_framework import serializers
from .models import Clase, Horario, Reserva
from .models import ListaEspera
from .serializers import ListaEsperaSerializer


class ClaseSerializer(serializers.ModelSerializer):
    instructor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Clase
        fields = ['id', 'nombre', 'descripcion', 'nivel', 'capacidad_maxima', 
                 'duracion_minutos', 'instructor', 'instructor_nombre', 'activa']
        read_only_fields = ['instructor_nombre']

    def get_instructor_nombre(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}" if obj.instructor else None

class HorarioSerializer(serializers.ModelSerializer):
    clase_nombre = serializers.CharField(source='clase.nombre', read_only=True)
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = Horario
        fields = ['id', 'clase', 'clase_nombre', 'dia_semana', 'dia_semana_display',
                 'hora_inicio', 'hora_fin', 'sala', 'cupos_disponibles']

class ReservaSerializer(serializers.ModelSerializer):
    clase_nombre = serializers.CharField(source='horario.clase.nombre', read_only=True)
    horario_display = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = ['id', 'usuario', 'horario', 'clase_nombre', 'horario_display',
                 'fecha', 'estado', 'fecha_creacion']
        read_only_fields = ['usuario', 'estado', 'fecha_creacion']

    def get_horario_display(self, obj):
        return f"{obj.horario.get_dia_semana_display()} {obj.horario.hora_inicio}"

class ListaEsperaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    clase_nombre = serializers.CharField(source='horario.clase.nombre', read_only=True)
    horario_display = serializers.SerializerMethodField()

    class Meta:
        model = ListaEspera
        fields = ['id', 'usuario', 'usuario_nombre', 'horario', 'clase_nombre', 
                 'horario_display', 'fecha', 'posicion', 'estado', 'fecha_registro']
        read_only_fields = ['usuario', 'posicion', 'estado', 'fecha_registro']

    def get_horario_display(self, obj):
        return f"{obj.horario.get_dia_semana_display()} {obj.horario.hora_inicio}"
