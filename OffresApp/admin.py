import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from config.admin_site import transconnect_admin_site
from .models import Offre


@admin.register(Offre, site=transconnect_admin_site)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        "expedition", "transporteur", "vehicule", "prix", "delai_jours",
        "statut", "statut_colore", "date_proposition",
    )
    list_filter = ("statut", "transporteur__raison_sociale", "date_proposition")
    search_fields = (
        "expedition__reference", "transporteur__raison_sociale", "vehicule__immatriculation",
    )
    list_editable = ("statut",)
    ordering = ("-created_at",)
    date_hierarchy = "date_proposition"
    list_per_page = 25
    autocomplete_fields = ("expedition", "transporteur", "vehicule")
    readonly_fields = ("date_proposition", "created_at", "updated_at", "statut_colore")
    fieldsets = (
        ("Détails de l'offre", {"fields": ("expedition", "transporteur", "vehicule")}),
        ("Conditions", {"fields": ("prix", "delai_jours")}),
        ("Suivi", {"fields": ("statut", "statut_colore", "date_proposition", "created_at", "updated_at")}),
    )
    actions = ("exporter_offres_csv",)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.statut == Offre.Statut.ACCEPTEE:
            fields.extend(("prix", "delai_jours"))
        return tuple(fields)

    @admin.display(description="Statut", ordering="statut")
    def statut_colore(self, obj):
        colors = {
            Offre.Statut.PROPOSEE: "#f0ad4e",
            Offre.Statut.ACCEPTEE: "#198754",
            Offre.Statut.REFUSEE: "#dc3545",
            Offre.Statut.RETIREE: "#6c757d",
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px">{}</span>',
            colors.get(obj.statut, "#999"),
            obj.get_statut_display(),
        )

    @admin.action(description="Exporter la sélection en CSV")
    def exporter_offres_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="offres.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(("reference_expedition", "transporteur", "prix", "statut"))
        for offre in queryset.select_related("expedition", "transporteur"):
            writer.writerow((
                offre.expedition.reference,
                offre.transporteur.raison_sociale,
                offre.prix,
                offre.statut,
            ))
        return response
