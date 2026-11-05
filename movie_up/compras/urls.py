from django.urls import path

from . import views

urlpatterns = [
    path('<int:pelicula_id>/', views.compra_pelicula, name='compra_pelicula'),
]
