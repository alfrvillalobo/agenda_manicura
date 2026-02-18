from django.urls import path
from clientes.views import editar_cliente, lista_clientes

urlpatterns = [
    path("", lista_clientes, name="lista_clientes"),
    path("editar/<int:cliente_id>/", editar_cliente, name="editar_cliente"),
]