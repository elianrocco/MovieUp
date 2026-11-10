from django.urls import path

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('<int:pk>/permisos/', views.cuenta_permiso_update, name='cuenta_permiso_update'),
]
