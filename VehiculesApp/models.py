from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = "camionnette", "Camionnette / utilitaire léger"
        FOURGON = "fourgon", "Fourgon"
        CAMION_PORTEUR = "camion_porteur", "Camion porteur"
        SEMI_REMORQUE = "semi_remorque", "Semi-remorque"

    # Capacités maximales indicatives du tableau du workshop Models (en kg).
    CAPACITE_MAX_PAR_TYPE = {
        TypeVehicule.CAMIONNETTE: 1500,
        TypeVehicule.FOURGON: 3500,
        TypeVehicule.CAMION_PORTEUR: 19000,
        TypeVehicule.SEMI_REMORQUE: 26000,
    }

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TypeVehicule.choices)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        "EntreprisesApp.Entreprise",
        on_delete=models.CASCADE,
        related_name="vehicules",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.capacite_kg is not None and self.capacite_kg <= 0:
            raise ValidationError({"capacite_kg": "La capacité doit être supérieure à zéro."})
        if self.entreprise_id:
            from EntreprisesApp.models import Entreprise

            entreprise = Entreprise.objects.filter(pk=self.entreprise_id).only("type_entreprise").first()
            if entreprise and entreprise.type_entreprise != Entreprise.TypeEntreprise.TRANSPORTEUR:
                raise ValidationError({"entreprise": "Un véhicule doit appartenir à un transporteur."})
        if self.pk and self.disponible and self.offres.filter(statut="acceptee").exists():
            raise ValidationError({"disponible": "Un véhicule affecté à une offre acceptée ne peut pas être disponible."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.immatriculation
