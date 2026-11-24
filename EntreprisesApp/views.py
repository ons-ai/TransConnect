"""Registration and company pages for TransConnect."""

from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from .forms import EntrepriseForm, InscriptionForm
from .mixins import EntrepriseACompleterMixin
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


class InscriptionView(CreateView):
    form_class = InscriptionForm
    template_name = "registration/inscription.html"
    success_url = reverse_lazy("entreprises:ajouter")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class EntrepriseCreateView(EntrepriseACompleterMixin, CreateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("expeditions:liste")

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        response = super().form_valid(form)
        # Keep the account's role aligned with the company it just registered.
        role = (
            self.request.user.Role.TRANSPORTEUR
            if self.object.type_entreprise == Entreprise.TypeEntreprise.TRANSPORTEUR
            else self.request.user.Role.CHARGEUR
        )
        if self.request.user.role != role:
            self.request.user.role = role
            self.request.user.save(update_fields=("role", "updated_at"))
        return response
