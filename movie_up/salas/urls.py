from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('', views.sala_list, name='sala_list'),
    path('<int:pk>/', views.sala_detail, name='sala_detail'),
    path('create/', views.sala_create, name='sala_create'),
    path('<int:pk>/update/', views.sala_update, name='sala_update'),
    path('<int:pk>/delete/', views.sala_delete, name='sala_delete'),
]
