from django.contrib import admin

from .models import Funcion


@admin.register(Funcion)
class FuncionAdmin(admin.ModelAdmin):
    list_display = (
        'pelicula',
        'sala',
        'inicio',
        'fin',
        'funcion_activa',
        'disponibilidad',
        'precio_entrada',
    )
