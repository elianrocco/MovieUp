from django.urls import path

from . import views


app_name = 'chatbot'

urlpatterns = [
    path('api/preguntar/', views.preguntar, name='preguntar'),
]
