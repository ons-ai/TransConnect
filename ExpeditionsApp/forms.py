from django import forms

from .models import Expedition


class ExpeditionForm(forms.ModelForm):
    """Publicly editable shipment fields; ownership and status stay server-side."""

    class Meta:
        model = Expedition
        fields = ("ville_depart", "ville_arrivee", "poids_kg", "date_souhaitee", "description")


class ExpeditionUpdateForm(ExpeditionForm):
    pass
