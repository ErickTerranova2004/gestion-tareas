from django.contrib import admin

from .models import Tarea


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "prioridad", "completada", "creada")
    list_filter = ("prioridad", "completada")
    search_fields = ("titulo",)
