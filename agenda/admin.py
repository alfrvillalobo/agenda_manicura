from django.contrib import admin
from .models import Cita, Pago


# ===============================
# INLINE DE PAGOS DENTRO DE CITA
# ===============================

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    readonly_fields = ("monto_formateado",)

    def monto_formateado(self, obj):
        if obj.pk:
            return "${:,.0f}".format(obj.monto).replace(",", ".")
        return ""

    monto_formateado.short_description = "Monto"


# ===============================
# ADMIN DE CITA
# ===============================

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "fecha",
        "hora_inicio",
        "estado",
        "precio_formateado",
        "total_pagado_formateado",
        "saldo_formateado",
    )

    list_filter = ("estado", "fecha")
    search_fields = ("cliente__nombre",)
    inlines = [PagoInline]

    # ---- Precio total ----
    def precio_formateado(self, obj):
        if obj.precio_total:
            return "${:,.0f}".format(obj.precio_total).replace(",", ".")
        return "-"

    precio_formateado.short_description = "Precio"

    # ---- Total pagado ----
    def total_pagado_formateado(self, obj):
        total = obj.total_pagado()
        if total:
            return "${:,.0f}".format(total).replace(",", ".")
        return "$0"

    total_pagado_formateado.short_description = "Total Pagado"

    # ---- Saldo pendiente ----
    def saldo_formateado(self, obj):
        saldo = obj.saldo_pendiente()
        if saldo is not None:
            return "${:,.0f}".format(saldo).replace(",", ".")
        return "-"

    saldo_formateado.short_description = "Saldo"


# ===============================
# ADMIN DE PAGOS
# ===============================

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("cita", "monto_formateado", "metodo", "fecha_pago")
    list_filter = ("metodo", "fecha_pago")

    def monto_formateado(self, obj):
        return "${:,.0f}".format(obj.monto).replace(",", ".")

    monto_formateado.short_description = "Monto"
