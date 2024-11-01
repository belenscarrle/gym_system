# config/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('gym_project')

# Configuración de tareas programadas
app.conf.beat_schedule = {
    'verificar-expiraciones-lista-espera': {
        'task': 'clases.tasks.verificar_expiraciones_lista_espera',  # Nombre completo de la tarea
        'schedule': crontab(hour=0, minute=0),  # Se ejecutará diariamente a medianoche
    },
}

app.conf.timezone = 'UTC'  # zona horaria
