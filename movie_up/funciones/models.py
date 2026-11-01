from django.db import models


class Funcion(models.Model):
    funcion_activa = models.BooleanField(default=False)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    idioma = models.CharField(max_length=45)
    subtitulada = models.BooleanField(default=False)
    distribucion = models.JSONField()
    disponibilidad = models.PositiveIntegerField()
    precio_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    pelicula = models.ForeignKey(
        'peliculas.Pelicula', on_delete=models.PROTECT, related_name='funciones'
    )
    sala = models.ForeignKey(
        'salas.Sala', on_delete=models.PROTECT, related_name='funciones'
    )
    entradas_compradas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.pelicula} - {self.sala} - {self.inicio}'
