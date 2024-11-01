# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo', 'is_staff')
    list_filter = ('tipo', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('tipo', 'telefono', 'fecha_nacimiento')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('tipo', 'telefono', 'fecha_nacimiento', 'email', 'first_name', 'last_name'),
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)