from django import forms

from .models import Vehicule


class VehiculeForm(forms.ModelForm):
    """Editable vehicle data; carrier ownership and availability are server-managed."""

    class Meta:
        model = Vehicule
        fields = ("immatriculation", "type_vehicule", "capacite_kg")
