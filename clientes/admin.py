from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono", "instagram", "activo", "fecha_registro")
    search_fields = ("nombre", "instagram")
    list_filter = ("activo",)
