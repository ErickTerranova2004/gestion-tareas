from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_tareas, name="lista_tareas"),
    path("tareas/<int:pk>/alternar/", views.alternar_tarea, name="alternar_tarea"),
    path("tareas/<int:pk>/eliminar/", views.eliminar_tarea, name="eliminar_tarea"),
    path("health/", views.health, name="health"),
]
