from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TareaForm
from .models import Tarea


def lista_tareas(request):
    if request.method == "POST":
        form = TareaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_tareas")
    else:
        form = TareaForm()

    tareas = Tarea.objects.all()
    contexto = {
        "form": form,
        "tareas": tareas,
        "pendientes": tareas.filter(completada=False).count(),
        "version": settings.APP_VERSION,
    }
    return render(request, "tareas/lista.html", contexto)


@require_POST
def alternar_tarea(request, pk):
    get_object_or_404(Tarea, pk=pk).alternar()
    return redirect("lista_tareas")


@require_POST
def eliminar_tarea(request, pk):
    get_object_or_404(Tarea, pk=pk).delete()
    return redirect("lista_tareas")


def health(request):
    """Endpoint de salud usado por Docker, el pipeline y el despliegue simulado."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db = "ok"
    except Exception:  # pragma: no cover - solo falla si la BD está caída
        db = "error"
    estado = 200 if db == "ok" else 503
    return JsonResponse(
        {"status": "ok" if db == "ok" else "degraded", "database": db, "version": settings.APP_VERSION},
        status=estado,
    )
