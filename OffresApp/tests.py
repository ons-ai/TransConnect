from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from config.admin_site import transconnect_admin_site
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from OffresApp.admin import OffreAdmin
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


class TransConnectModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.shipper_user = User.objects.create_user(
            username="shipper", email="shipper@gmail.com", password="pw",
            first_name="Sami", last_name="Chargeur",
        )
        self.carrier_user = User.objects.create_user(
            username="carrier", email="carrier@gmail.com", password="pw",
            first_name="Nadia", last_name="Transporteur", role=User.Role.TRANSPORTEUR,
        )
        self.other_carrier_user = User.objects.create_user(
            username="carrier2", email="carrier2@gmail.com", password="pw",
            first_name="Amir", last_name="Transporteur", role=User.Role.TRANSPORTEUR,
        )
        self.shipper = Entreprise.objects.create(
            raison_sociale="Chargeur de test",
            matricule_fiscal="1234567AAM000",
            type_entreprise=Entreprise.TypeEntreprise.CHARGEUR,
            adresse="12 avenue de test, Sousse, Tunisie",
            utilisateur=self.shipper_user,
        )
        self.carrier = Entreprise.objects.create(
            raison_sociale="Transporteur de test",
            matricule_fiscal="2345678BBP000",
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
            adresse="8 rue de test, Monastir, Tunisie",
            utilisateur=self.carrier_user,
        )
        self.other_carrier = Entreprise.objects.create(
            raison_sociale="Second transporteur",
            matricule_fiscal="3456789DAN000",
            type_entreprise=Entreprise.TypeEntreprise.TRANSPORTEUR,
            adresse="21 avenue de test, Tunis, Tunisie",
            utilisateur=self.other_carrier_user,
        )
        self.vehicle = Vehicule.objects.create(
            immatriculation="TU-TEST-1",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=self.carrier,
        )
        self.other_vehicle = Vehicule.objects.create(
            immatriculation="TU-TEST-2",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=self.other_carrier,
        )
        self.expedition = Expedition.objects.create(
            ville_depart="Lyon",
            ville_arrivee="Marseille",
            poids_kg=Decimal("1200.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=2),
            description="Palettes de test pour vérifier les contraintes.",
            entreprise=self.shipper,
        )

    def creer_offre(self, **changes):
        values = {
            "expedition": self.expedition,
            "transporteur": self.carrier,
            "vehicule": self.vehicle,
            "prix": Decimal("450.00"),
            "delai_jours": 2,
        }
        values.update(changes)
        return Offre.objects.create(**values)

    def test_user_identifier_and_gmail_validation(self):
        prefix = f"{timezone.localdate().year % 100:02d}user"
        self.assertEqual(
            [self.shipper_user.user_id, self.carrier_user.user_id, self.other_carrier_user.user_id],
            [f"{prefix}00", f"{prefix}01", f"{prefix}02"],
        )
        User = get_user_model()
        with self.assertRaises(ValidationError):
            User.objects.create_user(username="bad-email", email="bad@example.com", password="pw")

    def test_fiscal_number_and_address_are_validated(self):
        with self.assertRaises(ValidationError):
            Entreprise.objects.create(
                raison_sociale="Adresse trop courte",
                matricule_fiscal="123-invalid",
                type_entreprise=Entreprise.TypeEntreprise.CHARGEUR,
                adresse="trop court",
                utilisateur=get_user_model().objects.create_user(
                    username="short-address", email="short@gmail.com", password="pw"
                ),
            )

    def test_vehicle_requires_a_carrier_and_positive_capacity(self):
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(
                immatriculation="TU-SHIPPER",
                type_vehicule=Vehicule.TypeVehicule.FOURGON,
                capacite_kg=1000,
                entreprise=self.shipper,
            )
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(
                immatriculation="TU-ZERO",
                type_vehicule=Vehicule.TypeVehicule.FOURGON,
                capacite_kg=0,
                entreprise=self.carrier,
            )

    def test_expedition_reference_and_shipper_rule(self):
        self.assertRegex(self.expedition.reference, r"^EXP-\d{2}-\d{5}$")
        with self.assertRaises(ValidationError):
            Expedition.objects.create(
                ville_depart="Lyon", ville_arrivee="Nice", poids_kg=0,
                date_souhaitee=timezone.localdate(), entreprise=self.carrier,
            )

    def test_offer_rejects_non_carriers_unavailable_vehicles_and_bad_capacity(self):
        with self.assertRaises(ValidationError):
            self.creer_offre(transporteur=self.shipper)
        with self.assertRaises(ValidationError):
            self.creer_offre(vehicule=self.other_vehicle)

        unavailable = Vehicule.objects.create(
            immatriculation="TU-UNAVAILABLE",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            disponible=False,
            entreprise=self.carrier,
        )
        with self.assertRaises(ValidationError):
            self.creer_offre(vehicule=unavailable)
        with self.assertRaises(ValidationError):
            self.creer_offre(prix=Decimal("0.00"))
        with self.assertRaises(ValidationError):
            self.creer_offre(delai_jours=0)

        heavy_shipment = Expedition.objects.create(
            ville_depart="Lyon", ville_arrivee="Nice", poids_kg=Decimal("4000.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=3), entreprise=self.shipper,
        )
        with self.assertRaises(ValidationError):
            self.creer_offre(expedition=heavy_shipment)

    def test_only_one_active_proposal_per_carrier_and_shipment(self):
        self.creer_offre()
        with self.assertRaises(ValidationError):
            self.creer_offre(prix=Decimal("475.00"))

    def test_acceptance_assigns_shipment_refuses_other_offers_and_reserves_vehicle(self):
        accepted = self.creer_offre()
        rejected = self.creer_offre(transporteur=self.other_carrier, vehicule=self.other_vehicle)

        accepted.statut = Offre.Statut.ACCEPTEE
        accepted.save()

        self.expedition.refresh_from_db()
        self.vehicle.refresh_from_db()
        rejected.refresh_from_db()
        self.assertEqual(self.expedition.statut, Expedition.Statut.ATTRIBUEE)
        self.assertFalse(self.vehicle.disponible)
        self.assertEqual(rejected.statut, Offre.Statut.REFUSEE)

        self.vehicle.disponible = True
        with self.assertRaises(ValidationError):
            self.vehicle.save()

    def test_new_offer_requires_published_expedition(self):
        self.expedition.statut = Expedition.Statut.ATTRIBUEE
        self.expedition.save()
        with self.assertRaises(ValidationError):
            self.creer_offre()

    def test_health_check_is_staff_only_and_reports_model_integrity_checks(self):
        offer = self.creer_offre()
        Offre.objects.filter(pk=offer.pk).update(statut=Offre.Statut.ACCEPTEE)
        staff = get_user_model().objects.create_superuser(
            username="admin", email="admin@gmail.com", password="pw"
        )
        client = self.client
        response = client.get("/admin/health-check/")
        self.assertEqual(response.status_code, 302)

        client.force_login(staff)
        response = client.get("/admin/health-check/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Offres orphelines")
        self.assertContains(response, "Acceptations sans attribution")
        self.assertContains(response, "Transporteurs sans flotte")
        self.assertContains(response, "Doublons de propositions actives")
        self.assertEqual(len(response.context["checks"]), 6)
        self.assertEqual(response.context["checks"][0]["count"], 0)
        self.assertEqual(response.context["checks"][1]["count"], 1)
        self.assertEqual(response.context["checks"][4]["count"], 1)

    def test_admin_close_action_changes_only_in_progress_expeditions(self):
        in_progress = Expedition.objects.create(
            ville_depart="Tunis", ville_arrivee="Sousse", poids_kg=Decimal("800.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=1),
            statut=Expedition.Statut.EN_COURS, entreprise=self.shipper,
        )
        published = Expedition.objects.create(
            ville_depart="Tunis", ville_arrivee="Sfax", poids_kg=Decimal("900.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=1), entreprise=self.shipper,
        )
        request = RequestFactory().post("/admin/")
        request.user = get_user_model().objects.create_superuser(
            username="action-admin", email="action.admin@gmail.com", password="pw"
        )
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage

        request._messages = FallbackStorage(request)
        model_admin = transconnect_admin_site._registry[Expedition]
        model_admin.cloturer_expeditions(request, Expedition.objects.filter(pk__in=(in_progress.pk, published.pk)))

        in_progress.refresh_from_db()
        published.refresh_from_db()
        self.assertEqual(in_progress.statut, Expedition.Statut.LIVREE)
        self.assertEqual(published.statut, Expedition.Statut.PUBLIEE)

    def test_offers_csv_export_contains_selected_rows(self):
        offer = self.creer_offre()
        request = RequestFactory().post("/admin/")
        request.user = get_user_model().objects.create_superuser(
            username="csv-admin", email="csv.admin@gmail.com", password="pw"
        )
        model_admin = transconnect_admin_site._registry[Offre]
        response = model_admin.exporter_offres_csv(request, Offre.objects.filter(pk=offer.pk))
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn(self.expedition.reference.encode(), response.content)

    def test_admin_add_and_list_pages_render_for_all_five_models(self):
        staff = get_user_model().objects.create_superuser(
            username="pages-admin", email="pages.admin@gmail.com", password="pw"
        )
        self.client.force_login(staff)
        route_names = (
            "admin:EntreprisesApp_utilisateur_add",
            "admin:EntreprisesApp_utilisateur_changelist",
            "admin:EntreprisesApp_entreprise_add",
            "admin:EntreprisesApp_entreprise_changelist",
            "admin:VehiculesApp_vehicule_add",
            "admin:VehiculesApp_vehicule_changelist",
            "admin:ExpeditionsApp_expedition_add",
            "admin:ExpeditionsApp_expedition_changelist",
            "admin:OffresApp_offre_add",
            "admin:OffresApp_offre_changelist",
        )
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_admin_user_creation_generates_id_and_keeps_registration_role(self):
        staff = get_user_model().objects.create_superuser(
            username="create-user-admin", email="create.user.admin@gmail.com", password="pw"
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("admin:EntreprisesApp_utilisateur_add"),
            {
                "username": "new-carrier",
                "email": "new.carrier@gmail.com",
                "first_name": "Meriem",
                "last_name": "Transporteur",
                "telephone": "+216 20 000 111",
                "role": "transporteur",
                "password1": "V3ry-Strong-Test-Password!",
                "password2": "V3ry-Strong-Test-Password!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        created = get_user_model().objects.get(username="new-carrier")
        self.assertRegex(created.user_id, r"^\d{2}user\d{2}$")
        self.assertEqual(created.role, get_user_model().Role.TRANSPORTEUR)


class SeedDemoCommandTests(TestCase):
    def test_seed_command_creates_expected_scenarios_and_protects_existing_data(self):
        call_command("seed_demo", stdout=None)
        first = Expedition.objects.get(reference="EXP-26-00001")
        second = Expedition.objects.get(reference="EXP-26-00002")
        self.assertEqual(first.offres.filter(statut=Offre.Statut.PROPOSEE).count(), 2)
        self.assertEqual(second.offres.filter(statut=Offre.Statut.PROPOSEE).count(), 2)
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=None)
