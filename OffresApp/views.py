"""FBV reference views and CBV pages for offers."""

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from EntreprisesApp.mixins import TransporteurRequisMixin
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .forms import OffreForm, OffreUpdateForm
from .models import Offre


# FBV versions are kept as a reference for the migration to generic CBVs.
def liste_offres_fbv(request):
    offres = Offre.objects.select_related("expedition", "transporteur", "vehicule").order_by("-created_at")
    return render(request, "offres/liste.html", {"offres": offres})


def detail_offre_fbv(request, pk):
    offre = get_object_or_404(
        Offre.objects.select_related("expedition", "transporteur", "vehicule"), pk=pk
    )
    return render(request, "offres/detail.html", {"offre": offre})


class OffreListView(ListView):
    model = Offre
    template_name = "offres/liste.html"
    context_object_name = "offres"

    def get_queryset(self):
        return Offre.objects.select_related("expedition", "transporteur", "vehicule").order_by(
            "-created_at"
        )


class OffreDetailView(DetailView):
    model = Offre
    template_name = "offres/detail.html"
    context_object_name = "offre"

    def get_queryset(self):
        return Offre.objects.select_related("expedition", "transporteur", "vehicule")


class OffreCreateView(TransporteurRequisMixin, CreateView):
    model = Offre
    form_class = OffreForm
    template_name = "shared/form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["expedition"].queryset = Expedition.objects.filter(
            statut=Expedition.Statut.PUBLIEE
        ).select_related("entreprise")
        form.fields["vehicule"].queryset = Vehicule.objects.filter(
            entreprise=self.request.user.entreprise, disponible=True
        )
        return form

    def form_valid(self, form):
        # Carrier and status are deliberately absent from the submitted form.
        form.instance.transporteur = self.request.user.entreprise
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("expeditions:detail", kwargs={"reference": self.object.expedition.reference})


class OffreUpdateView(TransporteurRequisMixin, UpdateView):
    model = Offre
    form_class = OffreUpdateForm
    template_name = "shared/form.html"

    def get_queryset(self):
        return Offre.objects.filter(
            transporteur=self.request.user.entreprise,
            statut=Offre.Statut.PROPOSEE,
        ).select_related("transporteur")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("offres:detail", kwargs={"pk": self.object.pk})


class OffreDeleteView(TransporteurRequisMixin, DeleteView):
    model = Offre
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("offres:liste")

    def get_queryset(self):
        return Offre.objects.filter(
            transporteur=self.request.user.entreprise,
            statut=Offre.Statut.PROPOSEE,
        )


# Retained as a safe-method example from the FBV workshop; the active URL uses DeleteView.
@require_http_methods(["GET", "POST"])
def supprimer_offre_fbv(request, pk):
    offre = get_object_or_404(Offre, pk=pk, statut=Offre.Statut.PROPOSEE)
    if request.method == "POST":
        offre.delete()
        return redirect("offres:liste")
    return render(request, "shared/confirm_delete.html", {"object": offre})

