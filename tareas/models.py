from django.db import models


class Tarea(models.Model):
    PRIORIDADES = [
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta"),
    ]

    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=5, choices=PRIORIDADES, default="media")
    completada = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completada", "-creada"]

    def __str__(self):
        return self.titulo

    def alternar(self):
        """Cambia el estado de la tarea entre pendiente y completada."""
        self.completada = not self.completada
        self.save(update_fields=["completada"])
