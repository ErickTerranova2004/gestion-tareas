from django.test import TestCase
from django.urls import reverse

from .forms import TareaForm
from .models import Tarea


class TareaModelTests(TestCase):
    def test_str_devuelve_titulo(self):
        tarea = Tarea.objects.create(titulo="Configurar CI")
        self.assertEqual(str(tarea), "Configurar CI")

    def test_valores_por_defecto(self):
        tarea = Tarea.objects.create(titulo="Escribir Dockerfile")
        self.assertFalse(tarea.completada)
        self.assertEqual(tarea.prioridad, "media")

    def test_alternar_cambia_estado(self):
        tarea = Tarea.objects.create(titulo="Probar pipeline")
        tarea.alternar()
        tarea.refresh_from_db()
        self.assertTrue(tarea.completada)
        tarea.alternar()
        tarea.refresh_from_db()
        self.assertFalse(tarea.completada)

    def test_orden_pendientes_primero(self):
        hecha = Tarea.objects.create(titulo="Hecha", completada=True)
        pendiente = Tarea.objects.create(titulo="Pendiente")
        self.assertEqual(list(Tarea.objects.all()), [pendiente, hecha])


class TareaFormTests(TestCase):
    def test_titulo_corto_es_invalido(self):
        form = TareaForm(data={"titulo": "ab", "prioridad": "alta"})
        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)

    def test_formulario_valido(self):
        form = TareaForm(data={"titulo": "  Revisar PR  ", "prioridad": "baja"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["titulo"], "Revisar PR")


class TareaViewTests(TestCase):
    def test_lista_responde_200(self):
        Tarea.objects.create(titulo="Tarea visible")
        respuesta = self.client.get(reverse("lista_tareas"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Tarea visible")

    def test_crear_tarea_por_post(self):
        respuesta = self.client.post(
            reverse("lista_tareas"), {"titulo": "Nueva tarea", "prioridad": "alta"}
        )
        self.assertRedirects(respuesta, reverse("lista_tareas"))
        self.assertTrue(Tarea.objects.filter(titulo="Nueva tarea", prioridad="alta").exists())

    def test_alternar_por_post(self):
        tarea = Tarea.objects.create(titulo="Alternar")
        self.client.post(reverse("alternar_tarea", args=[tarea.pk]))
        tarea.refresh_from_db()
        self.assertTrue(tarea.completada)

    def test_alternar_por_get_no_permitido(self):
        tarea = Tarea.objects.create(titulo="Solo POST")
        respuesta = self.client.get(reverse("alternar_tarea", args=[tarea.pk]))
        self.assertEqual(respuesta.status_code, 405)

    def test_eliminar_tarea(self):
        tarea = Tarea.objects.create(titulo="Eliminar")
        self.client.post(reverse("eliminar_tarea", args=[tarea.pk]))
        self.assertFalse(Tarea.objects.filter(pk=tarea.pk).exists())

    def test_eliminar_inexistente_devuelve_404(self):
        respuesta = self.client.post(reverse("eliminar_tarea", args=[999]))
        self.assertEqual(respuesta.status_code, 404)


class HealthTests(TestCase):
    def test_health_reporta_bd_ok(self):
        respuesta = self.client.get(reverse("health"))
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["status"], "ok")
        self.assertEqual(datos["database"], "ok")
