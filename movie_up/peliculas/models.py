from django.db import models


class Pelicula(models.Model):
    titulo = models.CharField(max_length=150, unique=True)
    imagen_portada = models.ImageField(upload_to='imgs/')
    genero = models.CharField(max_length=45)
    duracion_minutos = models.PositiveIntegerField()
    descripcion = models.TextField()
    clasificacion = models.CharField(max_length=10)
    fecha_estreno = models.DateField()
    url_trailer = models.URLField(max_length=255)
    en_cartelera = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
