from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from config.admin_site import transconnect_admin_site
from .models import Entreprise, Utilisateur
from VehiculesApp.models import Vehicule


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ("immatriculation", "type_vehicule", "capacite_kg", "disponible")


@admin.register(Utilisateur, site=transconnect_admin_site)
class UtilisateurAdmin(UserAdmin):
    list_display = (
        "user_id",
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("user_id", "username", "email", "first_name", "last_name")
    list_editable = ("role", "is_active")
    ordering = ("-created_at",)
    date_hierarchy = "date_joined"
    list_per_page = 25
    readonly_fields = ("user_id", "last_login", "date_joined", "created_at", "updated_at")
    fieldsets = (
        ("Accès", {"fields": ("username", "password", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Identité", {"fields": ("user_id", "first_name", "last_name", "email", "telephone", "role")}),
        ("Dates", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "telephone", "role", "password1", "password2"),
        }),
    )


@admin.register(Entreprise, site=transconnect_admin_site)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ("raison_sociale", "matricule_fiscal", "type_entreprise", "utilisateur", "created_at")
    list_filter = ("type_entreprise",)
    search_fields = ("raison_sociale", "matricule_fiscal", "utilisateur__username", "utilisateur__email")
    list_editable = ("raison_sociale",)
    list_display_links = ("matricule_fiscal",)
    ordering = ("raison_sociale",)
    date_hierarchy = "created_at"
    list_per_page = 25
    autocomplete_fields = ("utilisateur",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identification", {"fields": ("raison_sociale", "matricule_fiscal", "type_entreprise")}),
        ("Adresse et compte", {"fields": ("adresse", "utilisateur")}),
        ("Suivi", {"fields": ("created_at", "updated_at")}),
    )
    inlines = (VehiculeInline,)
