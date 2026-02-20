from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from clientes.models import Cliente
from datetime import datetime, timedelta
from django.db.models import Sum

class Cita(models.Model):

    HORAS_DISPONIBLES = [
        (datetime.strptime("09:00", "%H:%M").time(), "09:00"),
        (datetime.strptime("15:00", "%H:%M").time(), "15:00"),
        (datetime.strptime("16:00", "%H:%M").time(), "16:00"),
        (datetime.strptime("18:00", "%H:%M").time(), "18:00"),
    ]

    ESTADOS = [
        ("reservada", "Reservada"),
        ("abono", "Abono"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(db_index=True)
    hora_inicio = models.TimeField()


    # Precio opcional (se puede definir después)
    precio_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="reservada"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]

    def __str__(self):
        fecha_formateada = self.fecha.strftime("%b %d %Y")
        hora_formateada = self.hora_inicio.strftime("%I %p").lower()
        return f"{self.cliente.nombre} - {fecha_formateada} - {hora_formateada}"

    def clean(self):
        """
        Reglas de negocio:
        - Máximo 3 citas activas por día
        - No repetir horario activo el mismo día
        """

        if self.estado == "cancelada":
            return

        citas_activas = Cita.objects.filter(
            fecha=self.fecha
        ).exclude(
            estado="cancelada"
        ).exclude(
            id=self.id
        )

        # Máximo 3 activas por día
        if citas_activas.count() >= 3:
            raise ValidationError("No se pueden agendar más de 3 citas activas por día.")

        # No repetir horario activo
        if citas_activas.filter(hora_inicio=self.hora_inicio).exists():
            raise ValidationError("Ya existe una cita activa en ese horario.")

    def ya_expirada(self):
        """
        Retorna True si han pasado más de 12 horas desde el inicio
        """
        inicio = datetime.combine(self.fecha, self.hora_inicio)
        inicio = timezone.make_aware(inicio)

        limite = inicio + timedelta(hours=12)
        return timezone.now() > limite

    # ---------------------------
    # MÉTODOS FINANCIEROS
    # ---------------------------

    def total_pagado(self):
        return self.pagos.aggregate(
            total=Sum("monto")
        )["total"] or 0

    def saldo_pendiente(self):
        if self.precio_total:
            return self.precio_total - self.total_pagado()
        return None


class Pago(models.Model):

    METODOS_PAGO = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("debito", "Débito"),
        ("credito", "Crédito"),
    ]

    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    metodo = models.CharField(
        max_length=20,
        choices=METODOS_PAGO
    )

    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        monto_formateado = "${:,.0f}".format(self.monto).replace(",", ".")
        return f"{monto_formateado} - {self.cita}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        cita = self.cita

        # Si la cita está cancelada no tocamos el estado
        if cita.estado == "cancelada":
            return

        total_pagado = cita.total_pagado()

        # Si no hay precio definido
        if cita.precio_total is None:
            if total_pagado > 0:
                cita.estado = "abono"
        else:
            if total_pagado == 0:
                cita.estado = "reservada"
            elif total_pagado < cita.precio_total:
                cita.estado = "abono"
            else:
                cita.estado = "pagado"

        cita.save()
