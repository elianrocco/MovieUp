from django.contrib import admin
from .models import Sala


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_sala', 'tipo_sonido', 'capacidad')
    search_fields = ('nombre',)
