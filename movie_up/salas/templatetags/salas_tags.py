from django import template


register = template.Library()

CELL_CLASS_MAP = {
    'P': 'celda--pasillo',
    'A': 'celda--asiento',
    'R': 'celda--reservado',
}


@register.filter
def celda_clase(value):
    return CELL_CLASS_MAP.get(value, 'celda--pasillo')
