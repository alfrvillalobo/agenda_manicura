from django.shortcuts import redirect, render
from django.db.models import Count
from .models import Cliente


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Max
from .models import Cliente


def lista_clientes(request):
    clientes = Cliente.objects.annotate(
        total_citas=Count("cita"),
        ultima_cita=Max("cita__fecha")
    ).order_by("nombre")

    return render(request, "clientes/lista_clientes.html", {
        "clientes": clientes
    })


def crear_cliente(request):
    if request.method == "POST":
        Cliente.objects.create(
            nombre=request.POST.get("nombre"),
            telefono=request.POST.get("telefono"),
            email=request.POST.get("email"),
            instagram=request.POST.get("instagram"),
            notas=request.POST.get("notas"),
        )
        return redirect("lista_clientes")

    return render(request, "clientes/crear_cliente.html")

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        cliente.nombre = request.POST.get("nombre")
        cliente.telefono = request.POST.get("telefono")
        cliente.email = request.POST.get("email")
        cliente.instagram = request.POST.get("instagram")
        cliente.notas = request.POST.get("notas")
        cliente.activo = True if request.POST.get("activo") == "on" else False
        cliente.save()
        return redirect("lista_clientes")

    return render(request, "clientes/editar_cliente.html", {
        "cliente": cliente
    })
