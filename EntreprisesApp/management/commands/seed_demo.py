from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


class Command(BaseCommand):
    help = "Crée un jeu de démonstration TransConnect avec deux expéditions et leurs offres."

    def handle(self, *args, **options):
        if Expedition.objects.filter(reference__in=("EXP-26-00001", "EXP-26-00002")).exists():
            raise CommandError("Les expéditions de démonstration existent déjà; aucune donnée n'a été modifiée.")

        User = get_user_model()
        shipper_user = User.objects.create_user(
            username="chargeur_demo",
            email="chargeur.demo@gmail.com",
            password=None,
            first_name="Sami",
            last_name="Ben Ali",
            telephone="+216 20 000 001",
            role=User.Role.CHARGEUR,
        )
        carrier_a_user = User.objects.create_user(
            username="transporteur_a",
            email="transporteur.a@gmail.com",
            password=None,
            first_name="Nadia",
            last_name="Trabelsi",
            telephone="+216 20 000 002",
            role=User.Role.TRANSPORTEUR,
        )
        carrier_b_user = User.objects.create_user(
            username="transporteur_b",
            email="transporteur.b@gmail.com",
            password=None,
            first_name="Karim",
            last_name="Mansour",
            telephone="+216 20 000 003",
            role=User.Role.TRANSPORTEUR,
        )

        shipper = Entreprise.objects.create(
            raison_sociale="Agroalimentaire du Sahel",
            matricule_fiscal="1234567AAM000",
            type_entreprise=Entreprise.TypeEntreprise.CHARGEUR,
            adresse="12 avenue Habib Bourguiba, Sousse, Tunisie",
            utilisateur=shipper_user,
        )
        carrier_a = Entreprise.objects.create(
            raison_sociale="Transport Rapide du Sahel",
            matricule_fiscal="2345678BBP000",
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
            adresse="8 rue de l'Industrie, Monastir, Tunisie",
            utilisateur=carrier_a_user,
        )
        carrier_b = Entreprise.objects.create(
            raison_sociale="Logistique Moderne de Tunis",
            matricule_fiscal="3456789DAN000",
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
            adresse="21 avenue de la Liberté, Tunis, Tunisie",
            utilisateur=carrier_b_user,
        )

        vehicle_a = Vehicule.objects.create(
            immatriculation="TU-1001",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=carrier_a,
        )
        vehicle_b = Vehicule.objects.create(
            immatriculation="TU-2002",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3200,
            entreprise=carrier_b,
        )
        vehicle_a_second = Vehicule.objects.create(
            immatriculation="TU-1002",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=carrier_a,
        )
        vehicle_b_second = Vehicule.objects.create(
            immatriculation="TU-2003",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3200,
            entreprise=carrier_b,
        )

        shipments = []
        for origin, destination, weight, days in (
            ("Lyon", "Marseille", Decimal("1200.00"), 2),
            ("Paris", "Lyon", Decimal("1800.00"), 3),
        ):
            shipments.append(
                Expedition.objects.create(
                    ville_depart=origin,
                    ville_arrivee=destination,
                    poids_kg=weight,
                    date_souhaitee=timezone.localdate() + timedelta(days=days),
                    description=f"Palettes de marchandises de {origin} à {destination}.",
                    entreprise=shipper,
                )
            )

        vehicle_assignments = (
            (vehicle_a, vehicle_b),
            (vehicle_a_second, vehicle_b_second),
        )
        for shipment, vehicles in zip(shipments, vehicle_assignments):
            for carrier, vehicle, price in (
                (carrier_a, vehicles[0], Decimal("450.00")),
                (carrier_b, vehicles[1], Decimal("490.00")),
            ):
                Offre.objects.create(
                    expedition=shipment,
                    transporteur=carrier,
                    vehicule=vehicle,
                    prix=price,
                    delai_jours=2,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Jeu de démonstration créé : {shipments[0].reference} et {shipments[1].reference}."
            )
        )
