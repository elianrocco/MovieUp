from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse

from . import services


def compra_pelicula(request, pelicula_id):
    if not request.user.is_authenticated:
        login_url = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": request.get_full_path()})}'
        )
        return redirect(login_url)

    if request.user.is_staff:
        return redirect('/gestion/')

    pelicula, funciones = services.preparar_compra(pelicula_id)
    return render(
        request,
        'compras/compra_pelicula.html',
        {'pelicula': pelicula, 'funciones': funciones},
    )


def seleccionar_asientos(request, pelicula_id, funcion_id):
    if not request.user.is_authenticated:
        login_url = (
            f'{reverse("google_login")}?'
            f'{urlencode({"process": "login", "next": request.get_full_path()})}'
        )
        return redirect(login_url)

    if request.user.is_staff:
        return redirect('/gestion/')

    funcion = services.obtener_funcion_vendible(pelicula_id, funcion_id)
    return render(
        request,
        'compras/seleccion_asientos.html',
        {
            'pelicula': funcion.pelicula,
            'funcion': funcion,
            'cuadricula': services.construir_cuadricula(funcion),
        },
    )
