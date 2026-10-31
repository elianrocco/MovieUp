from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    path('', views.pelicula_list, name='pelicula_list'),
    path('<int:pk>/', views.pelicula_detail, name='pelicula_detail'),
    path('create/', views.pelicula_create, name='pelicula_create'),
    path('<int:pk>/update/', views.pelicula_update, name='pelicula_update'),
    path('<int:pk>/delete/', views.pelicula_delete, name='pelicula_delete'),
]
