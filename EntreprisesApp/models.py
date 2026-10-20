import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


def validate_gmail_email(value):
    """Limit TransConnect accounts to the Gmail domain, regardless of case."""
    if value and value.rsplit("@", 1)[-1].lower() != "gmail.com":
        raise ValidationError("L'adresse e-mail doit appartenir au domaine gmail.com.")


class TransConnectUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Utilisateur.Role.CHARGEUR)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Utilisateur.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        CHARGEUR = "chargeur", "Chargeur"
        TRANSPORTEUR = "transporteur", "Transporteur"
        ADMIN = "admin", "Administrateur"

    user_id = models.CharField(max_length=8, primary_key=True, editable=False)
    email = models.EmailField(unique=True, validators=[validate_gmail_email])
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.CHARGEUR)
    telephone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransConnectUserManager()

    @classmethod
    def prochain_user_id(cls):
        prefix = f"{timezone.localdate().year % 100:02d}user"
        existing_ids = cls.objects.filter(user_id__startswith=prefix).values_list("user_id", flat=True)
        sequences = [int(user_id[-2:]) for user_id in existing_ids if len(user_id) == 8 and user_id[-2:].isdigit()]
        next_sequence = max(sequences, default=-1) + 1
        if next_sequence > 99:
            raise ValidationError("La limite de 100 comptes pour cette année est atteinte.")
        return f"{prefix}{next_sequence:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.prochain_user_id()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username


class Entreprise(models.Model):
    class TypeEntreprise(models.TextChoices):
        CHARGEUR = "chargeur", "Chargeur"
        TRANSPORTEUR = "transporteur", "Transporteur"

    raison_sociale = models.CharField(max_length=150)
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$",
                message="Le matricule fiscal tunisien n'a pas un format valide.",
            )
        ],
    )
    type_entreprise = models.CharField(max_length=15, choices=TypeEntreprise.choices)
    adresse = models.TextField(validators=[MinLengthValidator(20)])
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entreprise",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.adresse and len(self.adresse.strip()) < 20:
            raise ValidationError({"adresse": "L'adresse doit contenir au moins 20 caractères."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.raison_sociale
