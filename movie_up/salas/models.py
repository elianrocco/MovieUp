from django.db import models


class Sala(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    distribucion = models.JSONField()
    tipo_sala = models.CharField(max_length=45)
    tipo_sonido = models.CharField(max_length=45)
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre
