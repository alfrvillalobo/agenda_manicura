from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=120, db_index=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    instagram = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    notas = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
