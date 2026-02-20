import calendar
import datetime
from datetime import date, datetime
from django.shortcuts import get_object_or_404, render
from .models import Cita, Pago
from django.shortcuts import redirect
from .forms import CitaForm
from django.utils import timezone
from django.db.models import Sum, Value, F, DecimalField
from django.db.models.functions import Coalesce


def calendario_mensual(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))

    cal = calendar.monthcalendar(anio, mes)

    citas = Cita.objects.filter(fecha__year=anio, fecha__month=mes)

    conteo_citas = {}
    for cita in citas:
        dia = cita.fecha.day
        conteo_citas[dia] = conteo_citas.get(dia, 0) + 1

    # Construimos calendario enriquecido
    calendario_final = []

    for semana in cal:
        semana_datos = []
        for dia in semana:
            if dia == 0:
                semana_datos.append(None)
            else:
                cantidad = conteo_citas.get(dia, 0)

                if cantidad >= 3:
                    estado = "lleno"
                elif cantidad > 0:
                    estado = "medio"
                else:
                    estado = "vacio"

                semana_datos.append({
                    "dia": dia,
                    "cantidad": cantidad,
                    "estado": estado
                })

        calendario_final.append(semana_datos)

    # 🔁 Navegación mes anterior / siguiente
    if mes == 1:
        mes_anterior = 12
        anio_anterior = anio - 1
    else:
        mes_anterior = mes - 1
        anio_anterior = anio

    if mes == 12:
        mes_siguiente = 1
        anio_siguiente = anio + 1
    else:
        mes_siguiente = mes + 1
        anio_siguiente = anio

    contexto = {
        "calendario": calendario_final,
        "mes": mes,
        "anio": anio,
        "mes_anterior": mes_anterior,
        "anio_anterior": anio_anterior,
        "mes_siguiente": mes_siguiente,
        "anio_siguiente": anio_siguiente,
    }

    return render(request, "agenda/calendario.html", contexto)


def vista_dia(request, anio, mes, dia):
    fecha = datetime(anio, mes, dia).date()
    citas = Cita.objects.filter(fecha=fecha).order_by("hora_inicio")

    return render(request, "agenda/dia.html", {
        "fecha": fecha,
        "citas": citas
    })


from django.shortcuts import redirect
from .forms import CitaForm


def crear_cita(request, anio=None, mes=None, dia=None):
    fecha_inicial = None

    if anio and mes and dia:
        fecha_inicial = date(anio, mes, dia)

    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()

            # 🔁 Redirige al día después de guardar
            return redirect(
                "vista_dia",
                anio=anio,
                mes=mes,
                dia=dia
            )
    else:
        form = CitaForm(initial={"fecha": fecha_inicial})

    return render(
        request,
        "agenda/crear_cita.html",
        {
            "form": form,
            "anio": anio,
            "mes": mes,
            "dia": dia,
        }
    )

def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect("vista_dia", 
                            anio=cita.fecha.year, 
                            mes=cita.fecha.month, 
                            dia=cita.fecha.day)
    else:
        form = CitaForm(instance=cita)

    return render(request, "agenda/editar_cita.html", {
        "form": form,
        "cita": cita
    })

def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    fecha = cita.fecha

    if request.method == "POST":
        cita.delete()
        return redirect("vista_dia",
                        anio=fecha.year,
                        mes=fecha.month,
                        dia=fecha.day)

    return render(request, "agenda/eliminar_cita.html", {
        "cita": cita
    })

def registrar_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == "POST":
        monto = request.POST.get("monto")
        metodo = request.POST.get("metodo")

        Pago.objects.create(
            cita=cita,
            monto=monto,
            metodo=metodo
        )

        return redirect(
            "vista_dia",
            anio=cita.fecha.year,
            mes=cita.fecha.month,
            dia=cita.fecha.day
        )

    return render(request, "agenda/registrar_pago.html", {
        "cita": cita
    })
    

    
def dashboard_ingresos(request):
    hoy = timezone.now().date()

    # Obtener mes y año desde la URL
    anio = request.GET.get("anio")
    mes = request.GET.get("mes")

    if anio and mes:
        anio = int(anio)
        mes = int(mes)
    else:
        anio = hoy.year
        mes = hoy.month

    citas_mes = Cita.objects.filter(
        fecha__year=anio,
        fecha__month=mes
    )

    total_facturado = citas_mes.aggregate(
        total=Sum("precio_total")
    )["total"] or 0

    total_pagado = citas_mes.aggregate(
        total=Sum("pagos__monto")
    )["total"] or 0

    total_pendiente = total_facturado - total_pagado

    ingresos_por_dia = (
        citas_mes.values("fecha")
        .annotate(total=Sum("precio_total"))
        .order_by("fecha")
    )

    context = {
        "mes_nombre": calendar.month_name[mes],
        "mes": mes,
        "anio": anio,
        "total_facturado": total_facturado,
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
        "ingresos_por_dia": ingresos_por_dia,
    }

    return render(request, "agenda/dashboard.html", context)

from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

def detalle_pendientes(request):
    anio = int(request.GET.get("anio"))
    mes = int(request.GET.get("mes"))

    citas_mes = Cita.objects.filter(
        fecha__year=anio,
        fecha__month=mes
    ).annotate(
        total_pagado_calc=Coalesce(
            Sum("pagos__monto"),
            Value(0),
            output_field=DecimalField()
        ),
    ).annotate(
        saldo_calc=ExpressionWrapper(
            F("precio_total") - F("total_pagado_calc"),
            output_field=DecimalField()
        )
    )

    deudores = citas_mes.filter(
        precio_total__isnull=False,
        saldo_calc__gt=0
    )

    sin_precio = citas_mes.filter(
        precio_total__isnull=True
    )

    context = {
        "deudores": deudores,
        "sin_precio": sin_precio,
        "cantidad_deudores": deudores.count(),
        "cantidad_sin_precio": sin_precio.count(),
        "mes": mes,
        "anio": anio,
    }

    return render(request, "agenda/detalle_pendientes.html", context)
