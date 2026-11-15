from django.urls import path

from . import views

app_name = "offres"

urlpatterns = [
    path("", views.OffreListView.as_view(), name="liste"),
    path("ajouter/<int:entreprise_id>/", views.OffreCreateView.as_view(), name="ajouter"),
    path("<int:pk>/", views.OffreDetailView.as_view(), name="detail"),
    path("<int:pk>/modifier/<int:entreprise_id>/", views.OffreUpdateView.as_view(), name="modifier"),
    path("<int:pk>/supprimer/", views.OffreDeleteView.as_view(), name="supprimer"),
]
