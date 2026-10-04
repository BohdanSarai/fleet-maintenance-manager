from django.shortcuts import render

from django.views import generic
from .models import Vehicle


class IndexView(generic.TemplateView):
    template_name = "fleet/index.html"


class VehicleListView(generic.ListView):
    model = Vehicle
    context_object_name = "vehicle_list"


class VehicleDetailView(generic.DetailView):
    model = Vehicle


class VehicleCreateView(generic.CreateView):
    model = Vehicle
    fields = "__all__"
    