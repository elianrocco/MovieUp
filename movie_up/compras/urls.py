from django.urls import path

from . import views

app_name = 'compras'

urlpatterns = [
    path('<int:pelicula_id>/', views.compra_pelicula, name='compra_pelicula'),
    path(
        '<int:pelicula_id>/funciones/<int:funcion_id>/',
        views.seleccionar_asientos,
        name='seleccionar_asientos',
    ),
]
