from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule
from .models import Entreprise


class AuthenticationWorkflowTests(TestCase):
    def create_company(self, username, email, company_type, fiscal_number, *, password="Valid-Test-Password-42!"):
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            role=(
                get_user_model().Role.TRANSPORTEUR
                if company_type == Entreprise.TypeEntreprise.TRANSPORTEUR
                else get_user_model().Role.CHARGEUR
            ),
        )
        company = Entreprise.objects.create(
            raison_sociale=f"Entreprise {username}",
            matricule_fiscal=fiscal_number,
            type_entreprise=company_type,
            adresse="12 avenue des tests, Tunis, Tunisie",
            utilisateur=user,
        )
        return user, company

    def setUp(self):
        self.shipper_user, self.shipper = self.create_company(
            "shipper-auth", "shipper.auth@gmail.com", Entreprise.TypeEntreprise.CHARGEUR, "1111111AAM000"
        )
        self.carrier_user, self.carrier = self.create_company(
            "carrier-auth", "carrier.auth@gmail.com", Entreprise.TypeEntreprise.TRANSPORTEUR, "2222222BBP000"
        )
        self.other_shipper_user, self.other_shipper = self.create_company(
            "other-shipper", "other.shipper@gmail.com", Entreprise.TypeEntreprise.CHARGEUR, "3333333DAN000"
        )
        self.other_carrier_user, self.other_carrier = self.create_company(
            "other-carrier", "other.carrier@gmail.com", Entreprise.TypeEntreprise.TRANSPORTEUR, "4444444BBP000"
        )
        self.expedition = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal("900.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=4),
            description="Marchandise de test pour contrôler les permissions.",
            entreprise=self.shipper,
        )
        self.other_expedition = Expedition.objects.create(
            ville_depart="Sfax",
            ville_arrivee="Bizerte",
            poids_kg=Decimal("1000.00"),
            date_souhaitee=timezone.localdate() + timedelta(days=5),
            description="Seconde expédition pour tester la séparation des comptes.",
            entreprise=self.other_shipper,
        )
        self.vehicle = Vehicule.objects.create(
            immatriculation="TU-AUTH-1",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=self.carrier,
        )
        self.other_vehicle = Vehicule.objects.create(
            immatriculation="TU-AUTH-2",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3000,
            entreprise=self.other_carrier,
        )
        self.offer = Offre.objects.create(
            expedition=self.expedition,
            transporteur=self.carrier,
            vehicule=self.vehicle,
            prix=Decimal("450.00"),
            delai_jours=2,
        )
        self.other_offer = Offre.objects.create(
            expedition=self.other_expedition,
            transporteur=self.other_carrier,
            vehicule=self.other_vehicle,
            prix=Decimal("500.00"),
            delai_jours=3,
        )

    def test_login_redirects_back_and_logout_requires_post(self):
        protected_url = reverse("vehicules:ajouter")
        response = self.client.get(protected_url)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={protected_url}",
            fetch_redirect_response=False,
        )

        login_response = self.client.post(reverse("login"), {
            "username": self.carrier_user.username,
            "password": "Valid-Test-Password-42!",
            "next": protected_url,
        })
        self.assertRedirects(login_response, protected_url, fetch_redirect_response=False)
        self.assertEqual(
            self.client.get(protected_url).status_code,
            200,
        )

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        logout_response = self.client.post(reverse("logout"))
        self.assertRedirects(logout_response, reverse("expeditions:liste"), fetch_redirect_response=False)
        self.assertRedirects(
            self.client.get(protected_url),
            f"{reverse('login')}?next={protected_url}",
            fetch_redirect_response=False,
        )

    def test_signup_uses_user_creation_form_logs_in_and_never_exposes_privilege_fields(self):
        signup_url = reverse("inscription")
        response = self.client.get(signup_url)
        self.assertEqual(response.status_code, 200)
        fields = response.context["form"].fields
        self.assertEqual(set(fields), {"username", "email", "telephone", "password1", "password2"})
        self.assertNotIn("role", fields)
        self.assertNotIn("is_staff", fields)
        self.assertNotIn("is_superuser", fields)

        response = self.client.post(signup_url, {
            "username": "new-carrier",
            "email": "new.carrier@gmail.com",
            "telephone": "+216 20 111 222",
            "password1": "Strong-Registration-Password-58!",
            "password2": "Strong-Registration-Password-58!",
            "role": get_user_model().Role.ADMIN,
            "is_staff": "on",
            "is_superuser": "on",
        })
        self.assertRedirects(response, reverse("entreprises:ajouter"), fetch_redirect_response=False)
        user = get_user_model().objects.get(username="new-carrier")
        self.assertTrue(user.is_authenticated)
        self.assertNotEqual(user.password, "Strong-Registration-Password-58!")
        self.assertEqual(user.role, get_user_model().Role.CHARGEUR)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(self.client.get(reverse("entreprises:ajouter")).status_code, 200)

        response = self.client.post(reverse("entreprises:ajouter"), {
            "raison_sociale": "Nouveau transporteur",
            "matricule_fiscal": "5555555BBP000",
            "type_entreprise": Entreprise.TypeEntreprise.TRANSPORTEUR,
            "adresse": "15 rue des nouveaux transporteurs, Tunis",
            "utilisateur": self.shipper_user.pk,
        })
        self.assertRedirects(response, reverse("expeditions:liste"), fetch_redirect_response=False)
        company = Entreprise.objects.get(raison_sociale="Nouveau transporteur")
        user.refresh_from_db()
        self.assertEqual(company.utilisateur, user)
        self.assertEqual(user.role, get_user_model().Role.TRANSPORTEUR)
        self.assertEqual(self.client.session.get("_auth_user_id"), user.pk)

    def test_signup_rejects_non_gmail_email(self):
        response = self.client.post(reverse("inscription"), {
            "username": "bad-email",
            "email": "bad@example.com",
            "telephone": "",
            "password1": "Strong-Registration-Password-58!",
            "password2": "Strong-Registration-Password-58!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(get_user_model().objects.filter(username="bad-email").exists())

    def test_company_can_only_be_created_once_and_only_for_current_account(self):
        self.client.force_login(self.shipper_user)
        response = self.client.get(reverse("entreprises:ajouter"))
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(self.shipper.utilisateur, self.other_shipper_user)

    def test_role_mixins_return_forbidden_for_wrong_company_type(self):
        self.client.force_login(self.shipper_user)
        self.assertEqual(self.client.get(reverse("vehicules:ajouter")).status_code, 403)
        self.assertEqual(self.client.get(reverse("offres:ajouter")).status_code, 403)

        self.client.force_login(self.carrier_user)
        self.assertEqual(self.client.get(reverse("expeditions:ajouter")).status_code, 403)

    def test_vehicle_and_expedition_update_delete_only_load_the_current_company_objects(self):
        self.client.force_login(self.carrier_user)
        self.assertEqual(
            self.client.get(reverse("vehicules:modifier", kwargs={"pk": self.other_vehicle.pk})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("vehicules:supprimer", kwargs={"pk": self.other_vehicle.pk})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("vehicules:modifier", kwargs={"pk": self.vehicle.pk})).status_code,
            200,
        )

        self.client.force_login(self.other_shipper_user)
        self.assertEqual(
            self.client.get(reverse("expeditions:modifier", kwargs={"reference": self.expedition.reference})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("expeditions:supprimer", kwargs={"reference": self.expedition.reference})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("expeditions:modifier", kwargs={"reference": self.other_expedition.reference})).status_code,
            200,
        )

    def test_offer_update_and_delete_are_limited_to_own_active_proposals(self):
        self.client.force_login(self.carrier_user)
        self.assertEqual(
            self.client.get(reverse("offres:modifier", kwargs={"pk": self.other_offer.pk})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("offres:supprimer", kwargs={"pk": self.other_offer.pk})).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("offres:modifier", kwargs={"pk": self.offer.pk})).status_code, 200)

    def test_company_id_and_status_fields_are_ignored_when_forms_are_tampered(self):
        self.client.force_login(self.shipper_user)
        response = self.client.post(reverse("expeditions:ajouter"), {
            "ville_depart": "Tunis",
            "ville_arrivee": "Gabes",
            "poids_kg": "750.00",
            "date_souhaitee": (timezone.localdate() + timedelta(days=6)).isoformat(),
            "description": "Une expédition dont les champs protégés sont falsifiés.",
            "entreprise": self.other_shipper.pk,
            "statut": Expedition.Statut.ANNULEE,
        })
        self.assertEqual(response.status_code, 302)
        shipment = Expedition.objects.get(ville_arrivee="Gabes")
        self.assertEqual(shipment.entreprise, self.shipper)
        self.assertEqual(shipment.statut, Expedition.Statut.PUBLIEE)

        self.client.force_login(self.carrier_user)
        response = self.client.post(reverse("vehicules:ajouter"), {
            "immatriculation": "TU-AUTH-NEW",
            "type_vehicule": Vehicule.TypeVehicule.FOURGON,
            "capacite_kg": "2500",
            "entreprise": self.other_carrier.pk,
            "disponible": "false",
        })
        self.assertEqual(response.status_code, 302)
        vehicle = Vehicule.objects.get(immatriculation="TU-AUTH-NEW")
        self.assertEqual(vehicle.entreprise, self.carrier)
        self.assertTrue(vehicle.disponible)

        response = self.client.post(reverse("offres:ajouter"), {
            "expedition": self.other_expedition.pk,
            "vehicule": self.vehicle.pk,
            "prix": "475.00",
            "delai_jours": "3",
            "transporteur": self.other_carrier.pk,
            "statut": Offre.Statut.ACCEPTEE,
        })
        self.assertEqual(response.status_code, 302)
        offer = Offre.objects.get(expedition=self.other_expedition, transporteur=self.carrier)
        self.assertEqual(offer.statut, Offre.Statut.PROPOSEE)

    def test_navigation_and_password_change_pages_render(self):
        response = self.client.get(reverse("expeditions:liste"))
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("inscription"))

        self.client.force_login(self.carrier_user)
        response = self.client.get(reverse("expeditions:liste"))
        self.assertContains(response, reverse("vehicules:mes"))
        self.assertContains(response, reverse("password_change"))
        self.assertContains(response, reverse("logout"))
        self.assertEqual(self.client.get(reverse("password_change")).status_code, 200)
        response = self.client.post(reverse("password_change"), {
            "old_password": "Valid-Test-Password-42!",
            "new_password1": "A-New-Valid-Password-83!",
            "new_password2": "A-New-Valid-Password-83!",
        })
        self.assertRedirects(response, reverse("password_change_done"), fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("password_change_done")).status_code, 200)
        self.carrier_user.refresh_from_db()
        self.assertTrue(self.carrier_user.check_password("A-New-Valid-Password-83!"))

        self.client.force_login(self.shipper_user)
        response = self.client.get(reverse("expeditions:liste"))
        self.assertContains(response, reverse("expeditions:ajouter"))
        self.assertNotContains(response, reverse("vehicules:ajouter"))

    def test_complete_carrier_journey_signup_vehicle_offer_logout(self):
        password = "Journey-Password-73!"
        response = self.client.post(reverse("inscription"), {
            "username": "journey-carrier",
            "email": "journey.carrier@gmail.com",
            "telephone": "+216 22 333 444",
            "password1": password,
            "password2": password,
        })
        self.assertRedirects(response, reverse("entreprises:ajouter"), fetch_redirect_response=False)

        response = self.client.post(reverse("entreprises:ajouter"), {
            "raison_sociale": "Transporteur du parcours complet",
            "matricule_fiscal": "7777777BBP000",
            "type_entreprise": Entreprise.TypeEntreprise.TRANSPORTEUR,
            "adresse": "17 rue du parcours complet, Tunis",
        })
        self.assertRedirects(response, reverse("expeditions:liste"), fetch_redirect_response=False)
        user = get_user_model().objects.get(username="journey-carrier")
        company = user.entreprise
        self.assertEqual(user.role, get_user_model().Role.TRANSPORTEUR)

        response = self.client.post(reverse("vehicules:ajouter"), {
            "immatriculation": "TU-JOURNEY-1",
            "type_vehicule": Vehicule.TypeVehicule.FOURGON,
            "capacite_kg": 2800,
        })
        vehicle = Vehicule.objects.get(immatriculation="TU-JOURNEY-1")
        self.assertEqual(vehicle.entreprise, company)
        self.assertRedirects(
            response,
            reverse("vehicules:detail", kwargs={"pk": vehicle.pk}),
            fetch_redirect_response=False,
        )

        response = self.client.post(reverse("offres:ajouter"), {
            "expedition": self.expedition.pk,
            "vehicule": vehicle.pk,
            "prix": "620.00",
            "delai_jours": "3",
        })
        offer = Offre.objects.get(expedition=self.expedition, transporteur=company)
        self.assertEqual(offer.statut, Offre.Statut.PROPOSEE)
        self.assertRedirects(
            response,
            reverse("expeditions:detail", kwargs={"reference": self.expedition.reference}),
            fetch_redirect_response=False,
        )

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("expeditions:liste"), fetch_redirect_response=False)
        self.assertRedirects(
            self.client.get(reverse("vehicules:ajouter")),
            f"{reverse('login')}?next={reverse('vehicules:ajouter')}",
            fetch_redirect_response=False,
        )
