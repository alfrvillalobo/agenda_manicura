from django.urls import path

from clientes.views import crear_cliente, editar_cliente, lista_clientes
from .views import calendario_mensual, crear_cita, dashboard_ingresos, editar_cita, eliminar_cita, registrar_pago, vista_dia
from agenda import views

urlpatterns = [
    path("", calendario_mensual, name="calendario"),
    path("dia/<int:anio>/<int:mes>/<int:dia>/", vista_dia, name="vista_dia"),
    path("crear/", crear_cita, name="crear_cita"),
    path("crear/<int:anio>/<int:mes>/<int:dia>/", crear_cita, name="crear_cita_fecha"),
    path("editar/<int:cita_id>/", editar_cita, name="editar_cita"),
    path("eliminar/<int:cita_id>/", eliminar_cita, name="eliminar_cita"),
    path("pago/<int:cita_id>/", registrar_pago, name="registrar_pago"),
    path("clientes", lista_clientes, name="lista_clientes"),
    path("dashboard/", dashboard_ingresos, name="dashboard_ingresos"),
    path("nuevo/", crear_cliente, name="crear_cliente"),
    path("editar_cliente/<int:cliente_id>/", editar_cliente, name="editar_cliente"),
    path("pendientes/", views.detalle_pendientes, name="detalle_pendientes"),

]
