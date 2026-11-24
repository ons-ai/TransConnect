from django.urls import path

from . import views

app_name = "vehicules"

urlpatterns = [
    path("", views.VehiculeListView.as_view(), name="liste"),
    path("mes/", views.MesVehiculesView.as_view(), name="mes"),
    path("ajouter/", views.VehiculeCreateView.as_view(), name="ajouter"),
    path("<int:pk>/", views.VehiculeDetailView.as_view(), name="detail"),
    path("<int:pk>/modifier/", views.VehiculeUpdateView.as_view(), name="modifier"),
    path("<int:pk>/supprimer/", views.VehiculeDeleteView.as_view(), name="supprimer"),
]
