from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q


class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = "proposee", "Proposée"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"
        RETIREE = "retiree", "Retirée"

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.PROPOSEE)
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(
        "ExpeditionsApp.Expedition",
        on_delete=models.CASCADE,
        related_name="offres",
    )
    transporteur = models.ForeignKey(
        "EntreprisesApp.Entreprise",
        on_delete=models.CASCADE,
        related_name="offres",
    )
    vehicule = models.ForeignKey(
        "VehiculesApp.Vehicule",
        on_delete=models.CASCADE,
        related_name="offres",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("expedition", "transporteur"),
                condition=Q(statut="proposee"),
                name="unique_proposition_active_par_transporteur",
            )
        ]

    def clean(self):
        super().clean()
        current_status = None
        if self.pk and not self._state.adding:
            current_status = type(self).objects.filter(pk=self.pk).values_list("statut", flat=True).first()
        is_new = self._state.adding
        changing_to_proposed_or_accepted = self.statut in {
            self.Statut.PROPOSEE,
            self.Statut.ACCEPTEE,
        } and (is_new or current_status != self.statut)

        if self.transporteur_id:
            from EntreprisesApp.models import Entreprise

            transporteur = Entreprise.objects.filter(pk=self.transporteur_id).only("type_entreprise").first()
            if transporteur and transporteur.type_entreprise != Entreprise.TypeEntreprise.TRANSPORTEUR:
                raise ValidationError({"transporteur": "Seul un transporteur peut proposer une offre."})

        expedition = None
        if self.expedition_id:
            from ExpeditionsApp.models import Expedition

            expedition = Expedition.objects.filter(pk=self.expedition_id).only("statut", "poids_kg").first()
            if expedition and is_new and expedition.statut != Expedition.Statut.PUBLIEE:
                raise ValidationError({"expedition": "Une nouvelle offre exige une expédition publiée."})
            if (
                expedition
                and self.statut == self.Statut.ACCEPTEE
                and current_status != self.Statut.ACCEPTEE
                and expedition.statut != Expedition.Statut.PUBLIEE
            ):
                raise ValidationError({"expedition": "Seule une expédition publiée peut recevoir une offre acceptée."})

        vehicule = None
        if self.vehicule_id:
            from VehiculesApp.models import Vehicule

            vehicule = Vehicule.objects.filter(pk=self.vehicule_id).only(
                "entreprise_id", "disponible", "capacite_kg", "type_vehicule"
            ).first()
            if vehicule and self.transporteur_id and vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({"vehicule": "Le véhicule doit appartenir au transporteur de l'offre."})
            if vehicule and not vehicule.disponible and changing_to_proposed_or_accepted:
                raise ValidationError({"vehicule": "Un véhicule indisponible ne peut pas être proposé ou accepté."})
            if vehicule and expedition:
                capacite_type = Vehicule.CAPACITE_MAX_PAR_TYPE[vehicule.type_vehicule]
                capacite_reelle = min(vehicule.capacite_kg, capacite_type)
                if expedition.poids_kg > capacite_reelle:
                    raise ValidationError({"vehicule": "Le véhicule ne peut pas transporter le poids de cette expédition."})

        if self.statut == self.Statut.PROPOSEE and self.expedition_id and self.transporteur_id:
            autres_propositions = type(self).objects.filter(
                expedition_id=self.expedition_id,
                transporteur_id=self.transporteur_id,
                statut=self.Statut.PROPOSEE,
            )
            if self.pk:
                autres_propositions = autres_propositions.exclude(pk=self.pk)
            if autres_propositions.exists():
                raise ValidationError({"transporteur": "Ce transporteur a déjà une offre active pour cette expédition."})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            old_status = None
            if self.pk and not self._state.adding:
                old_status = type(self).objects.filter(pk=self.pk).values_list("statut", flat=True).first()
            self.full_clean()
            result = super().save(*args, **kwargs)

            if self.statut == self.Statut.ACCEPTEE and old_status != self.Statut.ACCEPTEE:
                from ExpeditionsApp.models import Expedition

                expedition = Expedition.objects.select_for_update().get(pk=self.expedition_id)
                expedition.statut = Expedition.Statut.ATTRIBUEE
                expedition.save()

                vehicule = self.vehicule
                vehicule.disponible = False
                vehicule.save()

                autres_offres = type(self).objects.filter(
                    expedition_id=self.expedition_id,
                    statut=self.Statut.PROPOSEE,
                ).exclude(pk=self.pk)
                for offre in autres_offres:
                    offre.statut = self.Statut.REFUSEE
                    offre.save()
            return result

    def __str__(self):
        return f"{self.expedition.reference} — {self.transporteur.raison_sociale}"
