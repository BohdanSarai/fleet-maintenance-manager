from django.db import transaction
from django.urls import reverse_lazy, reverse

from django.views import generic

from .forms import ChangeTiresForm
from .models import Vehicle, ServiceRecord, MaintenancePlan, TireInstallation, TireSet


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
        context["tire_installations"] = self.object.tire_installations.filter(removed_at_mileage__isnull=False)
        context["current_tire_installation"] = self.object.tire_installations.filter(removed_at_mileage__isnull=True).first()
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


class TireInstallationCreateView(generic.CreateView):
    model = TireInstallation
    fields = ("tire_set", "installed_at_mileage", )
    template_name = "fleet/tire_installation_form.html"

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        vehicle = Vehicle.objects.get(pk=self.kwargs["vehicle_pk"])
        form.instance.vehicle = vehicle
        installed_tire_sets = TireInstallation.objects.filter(
            removed_at_mileage__isnull=True
        ).values_list("tire_set_id", flat=True)
        form.fields["tire_set"].queryset = TireSet.objects.exclude(
            pk__in=installed_tire_sets
        )
        return form

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class ChangeTiresView(generic.FormView):
    form_class = ChangeTiresForm
    template_name = "fleet/change_tires_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        installed_tire_sets = TireInstallation.objects.filter(
            removed_at_mileage__isnull=True
        ).values_list("tire_set_id", flat=True)

        available_tire_sets = TireSet.objects.exclude(
            pk__in=installed_tire_sets
        )

        kwargs["tire_sets"] = available_tire_sets

        return kwargs

    def form_valid(self, form):
        vehicle = Vehicle.objects.get(pk=self.kwargs["vehicle_pk"])
        new_tire_set = form.cleaned_data["tire_set"]

        with transaction.atomic():
            current_installation = TireInstallation.objects.filter(
                vehicle=vehicle,
                removed_at_mileage__isnull=True
            ).first()

            if current_installation:
                current_installation.removed_at_mileage = vehicle.current_mileage
                current_installation.save()

            new_installation = TireInstallation(
                vehicle=vehicle,
                tire_set=new_tire_set,
                installed_at_mileage=vehicle.current_mileage,
            )

            new_installation.full_clean()
            new_installation.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "fleet:vehicle-detail",
            kwargs={"pk": self.kwargs["vehicle_pk"]}
        )


