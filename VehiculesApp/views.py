"""FBV reference views and CBV pages for the vehicle catalog."""

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from EntreprisesApp.models import Entreprise
from OffresApp.models import Offre
from .forms import VehiculeForm
from .models import Vehicule


# FBV versions are kept as a reference for the migration to generic CBVs.
def liste_vehicules_fbv(request):
    vehicules = Vehicule.objects.select_related("entreprise").order_by("immatriculation")
    return render(request, "vehicules/liste.html", {"vehicules": vehicules})


def detail_vehicule_fbv(request, pk):
    vehicule = get_object_or_404(Vehicule.objects.select_related("entreprise"), pk=pk)
    offres = vehicule.offres.select_related("expedition").order_by("-date_proposition")
    return render(request, "vehicules/detail.html", {"vehicule": vehicule, "offres": offres})


class VehiculeListView(ListView):
    model = Vehicule
    template_name = "vehicules/liste.html"
    context_object_name = "vehicules"

    def get_queryset(self):
        return Vehicule.objects.select_related("entreprise").order_by("immatriculation")


class VehiculeDetailView(DetailView):
    model = Vehicule
    template_name = "vehicules/detail.html"
    context_object_name = "vehicule"

    def get_queryset(self):
        return Vehicule.objects.select_related("entreprise")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offres"] = self.object.offres.select_related("expedition").order_by("-date_proposition")
        context["can_delete"] = not self.object.offres.filter(statut=Offre.Statut.ACCEPTEE).exists()
        return context


class VehiculeCreateView(CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = "shared/form.html"

    def get_entreprise_courante(self):
        return get_object_or_404(
            Entreprise,
            pk=self.kwargs["entreprise_id"],
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
        )

    def form_valid(self, form):
        form.instance.entreprise = self.get_entreprise_courante()
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("vehicules:detail", kwargs={"pk": self.object.pk})


class VehiculeUpdateView(UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = "shared/form.html"

    def get_queryset(self):
        return Vehicule.objects.filter(entreprise_id=self.kwargs["entreprise_id"])

    def form_valid(self, form):
        form.instance.entreprise = get_object_or_404(
            Entreprise,
            pk=self.kwargs["entreprise_id"],
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
        )
        try:
            return super().form_valid(form)
        except ValidationError as error:
            form.add_error(None, error.messages)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("vehicules:detail", kwargs={"pk": self.object.pk})


class VehiculeDeleteView(DeleteView):
    model = Vehicule
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("vehicules:liste")

    def get_queryset(self):
        return Vehicule.objects.exclude(offres__statut=Offre.Statut.ACCEPTEE)


@require_http_methods(["GET", "POST"])
def supprimer_vehicule_fbv(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == "POST":
        vehicule.delete()
        return redirect("vehicules:liste")
    return render(request, "shared/confirm_delete.html", {"object": vehicule})
