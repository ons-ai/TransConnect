from datetime import timedelta

from django.contrib.admin import AdminSite
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils import timezone


class TransConnectAdminSite(AdminSite):
    site_header = "Administration TransConnect"
    site_title = "TransConnect"
    index_title = "Pilotage des opérations"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "health-check/",
                self.admin_view(self.health_check),
                name="health_check",
            )
        ]
        return custom_urls + urls

    def health_check(self, request):
        from EntreprisesApp.models import Entreprise
        from ExpeditionsApp.models import Expedition
        from OffresApp.models import Offre
        from VehiculesApp.models import Vehicule

        orphan_offers = Offre.objects.select_related("expedition", "transporteur").filter(
            statut__in=(Offre.Statut.PROPOSEE, Offre.Statut.ACCEPTEE)
        ).exclude(
            expedition__statut__in=(Expedition.Statut.PUBLIEE, Expedition.Statut.ATTRIBUEE)
        )

        accepted_without_assignment = Offre.objects.select_related(
            "expedition", "transporteur"
        ).filter(statut=Offre.Statut.ACCEPTEE).exclude(
            expedition__statut=Expedition.Statut.ATTRIBUEE
        )

        cutoff = timezone.localdate() - timedelta(days=7)
        stalled_expeditions = Expedition.objects.filter(
            statut=Expedition.Statut.PUBLIEE,
            created_at__date__lt=cutoff,
        )

        transporters_without_fleet = (
            Entreprise.objects.filter(type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR)
            .annotate(nb_vehicules=Count("vehicules"))
            .filter(nb_vehicules=0)
        )

        available_but_assigned = Vehicule.objects.filter(
            disponible=True,
            offres__statut=Offre.Statut.ACCEPTEE,
        ).select_related("entreprise").distinct()

        duplicate_proposals = (
            Offre.objects.filter(statut=Offre.Statut.PROPOSEE)
            .values("expedition__reference", "transporteur__raison_sociale")
            .annotate(nombre=Count("pk"))
            .filter(nombre__gt=1)
            .order_by("expedition__reference", "transporteur__raison_sociale")
        )

        checks = [
            {
                "title": "Offres orphelines",
                "rule": "Une offre proposée ou acceptée doit concerner une expédition publiée ou attribuée.",
                "scenario": "Une mise à jour SQL en masse change le statut de l'expédition sans faire passer les offres par leurs méthodes de modèle.",
                "count": orphan_offers.count(),
                "items": [
                    f"{offer.pk} — {offer.expedition.reference}, {offer.transporteur.raison_sociale} ({offer.get_statut_display()})"
                    for offer in orphan_offers[:20]
                ],
            },
            {
                "title": "Acceptations sans attribution",
                "rule": "Toute offre acceptée doit avoir déclenché le passage de son expédition au statut attribuée.",
                "scenario": "Un .update(statut='acceptee') contourne la cascade de save() et laisse l'expédition publiée.",
                "count": accepted_without_assignment.count(),
                "items": [
                    f"{offer.pk} — {offer.expedition.reference} reste {offer.expedition.get_statut_display()} après acceptation"
                    for offer in accepted_without_assignment[:20]
                ],
            },
            {
                "title": "Expéditions publiées depuis plus de 7 jours",
                "rule": "Une expédition qui reste publiée plus de sept jours doit être examinée par les opérations.",
                "scenario": "Une publication est oubliée ou son statut n'est pas avancé après une absence de réponse des transporteurs.",
                "count": stalled_expeditions.count(),
                "items": [
                    f"{shipment.reference} — {shipment.ville_depart} → {shipment.ville_arrivee} (créée le {shipment.created_at:%d/%m/%Y})"
                    for shipment in stalled_expeditions[:20]
                ],
            },
            {
                "title": "Transporteurs sans flotte",
                "rule": "Une entreprise de type transporteur doit posséder au moins un véhicule pour répondre aux expéditions.",
                "scenario": "Un véhicule est supprimé en masse ou un transporteur est activé sans que sa flotte soit enregistrée.",
                "count": transporters_without_fleet.count(),
                "items": [f"{company.raison_sociale} — aucun véhicule" for company in transporters_without_fleet[:20]],
            },
            {
                "title": "Disponibilité incohérente",
                "rule": "Un véhicule affecté à une offre acceptée ne doit pas être marqué disponible.",
                "scenario": "Un import ou un .update() remet disponible=True après l'acceptation d'une offre.",
                "count": available_but_assigned.count(),
                "items": [
                    f"{vehicle.immatriculation} — {vehicle.entreprise.raison_sociale}"
                    for vehicle in available_but_assigned[:20]
                ],
            },
            {
                "title": "Doublons de propositions actives",
                "rule": "Un transporteur ne peut avoir qu'une offre proposée active par expédition.",
                "scenario": "Une ancienne migration ou un import effectué après désactivation de la contrainte unique laisse passer des doublons.",
                "count": duplicate_proposals.count(),
                "items": [
                    f"{row['expedition__reference']} — {row['transporteur__raison_sociale']} ({row['nombre']} offres)"
                    for row in duplicate_proposals[:20]
                ],
            },
        ]

        context = {
            **self.each_context(request),
            "title": "Contrôle d'intégrité TransConnect",
            "checks": checks,
            "cutoff_date": cutoff,
        }
        return TemplateResponse(request, "admin/health_check.html", context)


transconnect_admin_site = TransConnectAdminSite(name="admin")
