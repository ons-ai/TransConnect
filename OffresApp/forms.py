from django import forms

from .models import Offre


class OffreForm(forms.ModelForm):
    """Only the carrier's proposal data is client-editable."""

    class Meta:
        model = Offre
        fields = ("expedition", "vehicule", "prix", "delai_jours")


class OffreUpdateForm(forms.ModelForm):
    """A submitted offer may change its terms, but not its parties or status."""

    class Meta:
        model = Offre
        fields = ("prix", "delai_jours")
