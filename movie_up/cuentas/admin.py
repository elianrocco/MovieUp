from django.contrib import admin

from .models import Cuenta


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('correo', 'nombre')
    ordering = ('correo',)
    readonly_fields = ('correo', 'nombre')
    fields = ('correo', 'nombre', 'is_active', 'is_staff')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.is_superuser = obj.is_staff
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # TODO(entrada): Reject deletion when this account has associated tickets.
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # TODO(entrada): Reject bulk deletion when any account has associated tickets.
        super().delete_queryset(request, queryset)
