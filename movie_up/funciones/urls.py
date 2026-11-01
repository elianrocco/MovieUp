from django.urls import path

from . import views

app_name = 'funciones'

urlpatterns = [
    path('', views.funcion_list, name='funcion_list'),
    path('create/', views.funcion_create, name='funcion_create'),
    path('<int:pk>/', views.funcion_detail, name='funcion_detail'),
    path('<int:pk>/update/', views.funcion_update, name='funcion_update'),
    path('<int:pk>/delete/', views.funcion_delete, name='funcion_delete'),
]
