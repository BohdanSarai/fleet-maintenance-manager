from django.db.models import Model
from django.template.base import kwarg_re
from django.urls import reverse_lazy, reverse

from django.views import generic
from .models import Vehicle, ServiceRecord, MaintenancePlan


class IndexView(generic.TemplateView):
    template_name = "fleet/index.html"


class VehicleListView(generic.ListView):
    model = Vehicle
    context_object_name = "vehicle_list"


class VehicleDetailView(generic.DetailView):
    model = Vehicle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_records"] = self.object.service_records.all()
        context["maintenance_plans"] = self.object.maintenance_plans.all()
        return context


class VehicleCreateView(generic.CreateView):
    model = Vehicle
    fields = "__all__"


class VehicleUpdateView(generic.UpdateView):
    model = Vehicle
    fields = "__all__"


class VehicleDeleteView(generic.DeleteView):
    model = Vehicle
    success_url = reverse_lazy("fleet:vehicle-list")


class ServiceRecordCreateView(generic.CreateView):
    model = ServiceRecord
    fields = (
        "maintenance_plan",
        "name",
        "date",
        "mileage",
        "cost",
        "notes",
    )
    template_name = "fleet/service_record_form.html"


    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        vehicle = Vehicle.objects.get(pk=self.kwargs["pk"])
        form.instance.vehicle = vehicle
        form.fields["maintenance_plan"].queryset = MaintenancePlan.objects.filter(vehicle=vehicle)
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.object.vehicle.pk
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class ServiceRecordUpdateView(generic.UpdateView):
    model = ServiceRecord
    fields = (
        "maintenance_plan",
        "name",
        "date",
        "mileage",
        "cost",
        "notes",
    )
    template_name = "fleet/service_record_form.html"
    pk_url_kwarg = "service_record_pk"

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        vehicle = Vehicle.objects.get(pk=self.kwargs["vehicle_pk"])
        form.instance.vehicle = vehicle
        form.fields["maintenance_plan"].queryset = MaintenancePlan.objects.filter(vehicle=vehicle)
        return form

    def get_success_url(self):
        pk = self.object.vehicle.pk
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class ServiceRecordDeleteView(generic.DeleteView):
    model = ServiceRecord
    pk_url_kwarg = "service_record_pk"
    template_name = "fleet/service_record_confirm_delete.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanCreateView(generic.CreateView):
    model = MaintenancePlan
    fields = ("name", "mileage_interval", "time_interval_months", )
    template_name = "fleet/maintenance_plan_form.html"


    def form_valid(self, form):
        vehicle = Vehicle.objects.get(pk=self.kwargs["vehicle_pk"])
        form.instance.vehicle = vehicle
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanUpdateView(generic.UpdateView):
    model = MaintenancePlan
    fields = ("name", "mileage_interval", "time_interval_months", )
    pk_url_kwarg = "maintenance_plan_pk"
    template_name = "fleet/maintenance_plan_form.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanDeleteView(generic.DeleteView):
    model = MaintenancePlan
    pk_url_kwarg = "maintenance_plan_pk"
    template_name = "fleet/maintenance_plan_confirm_delete.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})




