from django import forms

from .models import Tarea


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "descripcion", "prioridad"]
        widgets = {
            "titulo": forms.TextInput(attrs={"placeholder": "¿Qué hay que hacer?"}),
            "descripcion": forms.Textarea(attrs={"rows": 2, "placeholder": "Detalle (opcional)"}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 3:
            raise forms.ValidationError("El título debe tener al menos 3 caracteres.")
        return titulo
