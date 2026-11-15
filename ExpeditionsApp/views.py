"""FBV reference views and CBV pages for shipment workflows."""

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from EntreprisesApp.models import Entreprise
from .forms import ExpeditionForm, ExpeditionUpdateForm
from .models import Expedition


# FBV versions are kept as a reference for the migration to generic CBVs.
def liste_expeditions_fbv(request):
    expeditions = (
        Expedition.objects.filter(statut=Expedition.Statut.PUBLIEE)
        .select_related("entreprise")
        .order_by("-created_at")
    )
    return render(request, "expeditions/liste.html", {"expeditions": expeditions})


def detail_expedition_fbv(request, reference):
    expedition = get_object_or_404(Expedition.objects.select_related("entreprise"), reference=reference)
    offres = expedition.offres.select_related("transporteur", "vehicule").order_by("-date_proposition")
    return render(request, "expeditions/detail.html", {"expedition": expedition, "offres": offres})


class ExpeditionListView(ListView):
    model = Expedition
    template_name = "expeditions/liste.html"
    context_object_name = "expeditions"

    def get_queryset(self):
        return (
            Expedition.objects.filter(statut=Expedition.Statut.PUBLIEE)
            .select_related("entreprise")
            .order_by("-created_at")
        )


class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = "expeditions/detail.html"
    context_object_name = "expedition"
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get_queryset(self):
        return Expedition.objects.select_related("entreprise")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offres"] = self.object.offres.select_related("transporteur", "vehicule").order_by(
            "-date_proposition"
        )
        return context


class ExpeditionCreateView(CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = "shared/form.html"

    def get_entreprise_courante(self):
        return get_object_or_404(
            Entreprise,
            pk=self.kwargs["entreprise_id"],
            type_entreprise=Entreprise.TypeEntreprise.CHARGEUR,
        )

    def form_valid(self, form):
        form.instance.entreprise = self.get_entreprise_courante()
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("expeditions:detail", kwargs={"reference": self.object.reference})


class ExpeditionUpdateView(UpdateView):
    model = Expedition
    form_class = ExpeditionUpdateForm
    template_name = "shared/form.html"
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get_queryset(self):
        return Expedition.objects.filter(entreprise_id=self.kwargs["entreprise_id"])

    def form_valid(self, form):
        form.instance.entreprise = get_object_or_404(
            Entreprise,
            pk=self.kwargs["entreprise_id"],
            type_entreprise=Entreprise.TypeEntreprise.CHARGEUR,
        )
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("expeditions:detail", kwargs={"reference": self.object.reference})


class ExpeditionDeleteView(DeleteView):
    model = Expedition
    template_name = "shared/confirm_delete.html"
    slug_field = "reference"
    slug_url_kwarg = "reference"
    success_url = reverse_lazy("expeditions:liste")


# Retained as a safe-method example from the FBV workshop; the active URL uses DeleteView.
@require_http_methods(["GET", "POST"])
def supprimer_expedition_fbv(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    if request.method == "POST":
        expedition.delete()
        return redirect("expeditions:liste")
    return render(request, "shared/confirm_delete.html", {"object": expedition})
