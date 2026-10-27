from .views import *
from django.urls import path

urlpatterns = [
    path('home/', home, name='home'),
    path('w/<str:name>/', welcome, name='welcomeFunction'),
    path('list/', list_expeditions, name='list_expeditions'),
    path('details/<int:id>/', detail_expedition, name='detail_expedition')
]