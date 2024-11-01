# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPOS = (
        ('admin', 'Administrador'),
        ('miembro', 'Miembro'),
    )
    
    tipo = models.CharField(max_length=20, choices=TIPOS, default='miembro')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username