from django.urls import path

from . import views

app_name = 'entradas'

urlpatterns = [
    path('', views.entrada_list, name='entrada_list'),
    path('validar/', views.entrada_validar, name='entrada_validar'),
    path('<int:pk>/', views.entrada_detail, name='entrada_detail'),
]
