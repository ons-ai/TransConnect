from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from config.admin_site import transconnect_admin_site
from OffresApp.models import Offre
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = "en retard"
    parameter_name = "en_retard"

    def lookups(self, request, model_admin):
        return (("oui", "Oui"), ("non", "Non"))

    def queryset(self, request, queryset):
        overdue = {"statut": Expedition.Statut.PUBLIEE, "date_souhaitee__lt": timezone.localdate()}
        if self.value() == "oui":
            return queryset.filter(**overdue)
        if self.value() == "non":
            return queryset.exclude(**overdue)
        return queryset


class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = "expedition"
    readonly_fields = ("transporteur", "vehicule", "prix", "delai_jours", "statut", "date_proposition")
    fields = readonly_fields
    show_change_link = True
    can_delete = False


@admin.register(Expedition, site=transconnect_admin_site)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "entreprise", "ville_depart", "ville_arrivee", "poids_kg",
        "statut", "statut_colore", "date_souhaitee",
    )
    list_filter = ("statut", "ville_depart", EnRetardFilter)
    search_fields = ("reference", "entreprise__raison_sociale", "ville_depart", "ville_arrivee")
    list_editable = ("statut",)
    ordering = ("-created_at",)
    date_hierarchy = "date_souhaitee"
    list_per_page = 25
    autocomplete_fields = ("entreprise",)
    readonly_fields = ("reference", "statut_colore", "created_at", "updated_at")
    fieldsets = (
        ("Trajet", {"fields": ("reference", "entreprise", "ville_depart", "ville_arrivee")}),
        ("Marchandise", {"fields": ("poids_kg", "date_souhaitee", "description")}),
        ("Suivi", {"fields": ("statut", "statut_colore", "created_at", "updated_at")}),
    )
    inlines = (OffreInline,)
    actions = ("cloturer_expeditions",)

    @admin.display(description="Statut", ordering="statut")
    def statut_colore(self, obj):
        colors = {
            Expedition.Statut.PUBLIEE: "#0d6efd",
            Expedition.Statut.ATTRIBUEE: "#6f42c1",
            Expedition.Statut.EN_COURS: "#fd7e14",
            Expedition.Statut.LIVREE: "#198754",
            Expedition.Statut.ANNULEE: "#6c757d",
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px">{}</span>',
            colors.get(obj.statut, "#777"),
            obj.get_statut_display(),
        )

    @admin.action(description="Clôturer les expéditions sélectionnées (en cours → livrées)")
    def cloturer_expeditions(self, request, queryset):
        count = 0
        for expedition in queryset:
            if expedition.statut != Expedition.Statut.EN_COURS:
                continue
            expedition.statut = Expedition.Statut.LIVREE
            expedition.full_clean()
            expedition.save()
            count += 1
        self.message_user(request, f"{count} expédition(s) clôturée(s).")
