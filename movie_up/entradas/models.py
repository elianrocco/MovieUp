from django.db import models


class Entrada(models.Model):
    funcion = models.ForeignKey(
        'funciones.Funcion', on_delete=models.PROTECT, related_name='entradas'
    )
    cuenta = models.ForeignKey(
        'cuentas.Cuenta', on_delete=models.PROTECT, related_name='entradas'
    )
    codigo = models.CharField(max_length=12, unique=True)
    l_fila = models.CharField(max_length=4)
    n_asiento = models.PositiveSmallIntegerField()
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'entrada'
        constraints = [
            models.UniqueConstraint(
                fields=['funcion', 'l_fila', 'n_asiento'],
                name='uq_entrada_asiento',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.funcion}'
