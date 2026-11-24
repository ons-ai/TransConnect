from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Entreprise


class TransporteurRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require an authenticated account linked to a carrier company."""

    def test_func(self):
        entreprise = getattr(self.request.user, "entreprise", None)
        return entreprise is not None and entreprise.type_entreprise == Entreprise.TypeEntreprise.TRANSPORTEUR


class ChargeurRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require an authenticated account linked to a shipper company."""

    def test_func(self):
        entreprise = getattr(self.request.user, "entreprise", None)
        return entreprise is not None and entreprise.type_entreprise == Entreprise.TypeEntreprise.CHARGEUR


class EntrepriseACompleterMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only accounts without a company may create their one-to-one company."""

    def test_func(self):
        return not hasattr(self.request.user, "entreprise")
