"""FBV reference views and CBV pages for companies."""

from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Entreprise


# FBV versions are kept as a reference for the migration to generic CBVs.
def liste_entreprises_fbv(request):
    entreprises = Entreprise.objects.select_related("utilisateur").order_by("raison_sociale")
    return render(request, "entreprises/liste.html", {"entreprises": entreprises})


def detail_entreprise_fbv(request, pk):
    entreprise = get_object_or_404(Entreprise.objects.select_related("utilisateur"), pk=pk)
    return render(request, "entreprises/detail.html", {"entreprise": entreprise})


class EntrepriseListView(ListView):
    model = Entreprise
    template_name = "entreprises/liste.html"
    context_object_name = "entreprises"

    def get_queryset(self):
        return Entreprise.objects.select_related("utilisateur").order_by("raison_sociale")


class EntrepriseDetailView(DetailView):
    model = Entreprise
    template_name = "entreprises/detail.html"
    context_object_name = "entreprise"

    def get_queryset(self):
        return Entreprise.objects.select_related("utilisateur")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.type_entreprise == Entreprise.TypeEntreprise.TRANSPORTEUR:
            context["vehicules"] = self.object.vehicules.order_by("immatriculation")
        else:
            context["expeditions"] = self.object.expeditions.order_by("-created_at")
        return context
