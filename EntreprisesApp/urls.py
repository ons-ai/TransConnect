from django.urls import path

from . import views

app_name = "entreprises"

urlpatterns = [
    path("", views.EntrepriseListView.as_view(), name="liste"),
    path("<int:pk>/", views.EntrepriseDetailView.as_view(), name="detail"),
]
