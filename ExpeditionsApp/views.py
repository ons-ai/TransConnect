from django.shortcuts import render
from django.http import HttpResponse
from .models import Expedition
# Create your views here.

def home(request):
    return HttpResponse("<h1> Welcome To ... </h1>")
def welcome(request, name):
    return HttpResponse(f"hello {name}!")
def list_expeditions(request):
    return render(request, 'expedition/list.html')
def detail_expedition(request, id):
    expedition = Expedition.objects.get(id=id)
    return render(request, 'expedition/detail.html', {'expedition': expedition})

