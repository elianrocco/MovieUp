from django.contrib import admin

from .models import Entrada


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'funcion', 'cuenta', 'l_fila', 'n_asiento', 'activa')
    list_select_related = ('funcion', 'cuenta')
    ordering = ('-pk',)
    readonly_fields = ('funcion', 'cuenta', 'codigo', 'l_fila', 'n_asiento', 'activa')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
