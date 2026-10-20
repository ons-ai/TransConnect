from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = "publiee", "Publiée"
        ATTRIBUEE = "attribuee", "Attribuée"
        EN_COURS = "en_cours", "En cours"
        LIVREE = "livree", "Livrée"
        ANNULEE = "annulee", "Annulée"

    reference = models.CharField(max_length=12, unique=True, blank=True, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.PUBLIEE)
    entreprise = models.ForeignKey(
        "EntreprisesApp.Entreprise",
        on_delete=models.CASCADE,
        related_name="expeditions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def prochaine_reference(cls):
        prefix = f"EXP-{timezone.localdate().year % 100:02d}-"
        existing = cls.objects.filter(reference__startswith=prefix).values_list("reference", flat=True)
        sequences = [int(reference[-5:]) for reference in existing if reference[-5:].isdigit()]
        next_sequence = max(sequences, default=0) + 1
        if next_sequence > 99999:
            raise ValidationError("La limite annuelle de références d'expédition est atteinte.")
        return f"{prefix}{next_sequence:05d}"

    def clean(self):
        super().clean()
        if self.poids_kg is not None and self.poids_kg <= 0:
            raise ValidationError({"poids_kg": "Le poids doit être supérieur à zéro."})
        if self.entreprise_id:
            from EntreprisesApp.models import Entreprise

            entreprise = Entreprise.objects.filter(pk=self.entreprise_id).only("type_entreprise").first()
            if entreprise and entreprise.type_entreprise != Entreprise.TypeEntreprise.CHARGEUR:
                raise ValidationError({"entreprise": "Une expédition doit appartenir à un chargeur."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.prochaine_reference()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference
