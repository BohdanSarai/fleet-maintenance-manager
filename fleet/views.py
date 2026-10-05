from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from django.views import generic

from .forms import ChangeTiresForm, VehicleSearchForm, EmployeeCreationForm, VehicleMileageUpdateForm, \
    MaintenancePlanForm, ServiceRecordForm, TireSetForm
from .models import Vehicle, ServiceRecord, MaintenancePlan, TireInstallation, TireSet, CompanyUser


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "fleet/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        maintenance_reminders = []
        today = timezone.localdate()

        plans = MaintenancePlan.objects.select_related("vehicle")

        for plan in plans:
            next_mileage = plan.get_next_service_mileage()
            next_date = plan.get_next_service_date()

            mileage_left = None
            days_left = None

            if next_mileage is not None:
                mileage_left = (
                    next_mileage - plan.vehicle.current_mileage
                )

            if next_date is not None:
                days_left = (next_date - today).days

            mileage_due = (
                mileage_left is not None
                and mileage_left <= 1000
            )

            date_due = (
                days_left is not None
                and days_left <= 30
            )

            if mileage_due or date_due:
                maintenance_reminders.append({
                    "plan": plan,
                    "next_mileage": next_mileage,
                    "next_date": next_date,
                    "mileage_left": mileage_left,
                    "days_left": days_left,
                    "overdue_mileage": (
                        abs(mileage_left)
                        if mileage_left is not None and mileage_left < 0
                        else None
                    ),
                    "overdue_days": (
                        abs(days_left)
                        if days_left is not None and days_left < 0
                        else None
                    ),
                })

        context["maintenance_reminders"] = maintenance_reminders

        context["active_vehicles_count"] = Vehicle.objects.filter(
            is_active=True
        ).count()

        context["active_employees_count"] = CompanyUser.objects.filter(
            is_owner=False,
            is_active=True,
        ).count()

        context["service_records_count"] = ServiceRecord.objects.count()

        context["tire_sets_count"] = TireSet.objects.count()

        return context


class VehicleListView(LoginRequiredMixin, generic.ListView):
    model = Vehicle
    context_object_name = "vehicle_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()

        form = VehicleSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data["query"]

            if query:
                queryset = queryset.filter(
                    Q(brand__icontains=query)
                    | Q(model__icontains=query)
                    | Q(license_plate__icontains=query)
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = VehicleSearchForm(
            initial={"query": self.request.GET.get("query", "")}
        )
        return context


class VehicleDetailView(LoginRequiredMixin, generic.DetailView):
    model = Vehicle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_records"] = self.object.service_records.all()
        context["maintenance_plans"] = self.object.maintenance_plans.all()
        context["tire_installations"] = self.object.tire_installations.filter(removed_at_mileage__isnull=False)
        context["current_tire_installation"] = self.object.tire_installations.filter(removed_at_mileage__isnull=True).first()
        return context


class VehicleCreateView(LoginRequiredMixin, generic.CreateView):
    model = Vehicle
    fields = (
        "brand",
        "model",
        "year",
        "license_plate",
        "vin",
        "fuel_type",
        "current_mileage",
    )


class VehicleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Vehicle
    fields = (
        "brand",
        "model",
        "year",
        "license_plate",
        "vin",
        "fuel_type",
        "current_mileage",
        "is_active",
    )


class VehicleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Vehicle
    success_url = reverse_lazy("fleet:vehicle-list")


class ServiceRecordCreateView(LoginRequiredMixin, generic.CreateView):
    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = "fleet/service_record_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        vehicle = Vehicle.objects.get(
            pk=self.kwargs["vehicle_pk"]
        )

        form.instance.vehicle = vehicle

        form.fields["maintenance_plan"].queryset = (
            MaintenancePlan.objects.filter(vehicle=vehicle)
        )

        form.fields["mileage"].initial = vehicle.current_mileage

        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.object.vehicle.pk
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class ServiceRecordUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = ServiceRecord
    form_class = ServiceRecordForm
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


class ServiceRecordDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = ServiceRecord
    pk_url_kwarg = "service_record_pk"
    template_name = "fleet/service_record_confirm_delete.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanCreateView(LoginRequiredMixin, generic.CreateView):
    model = MaintenancePlan
    form_class = MaintenancePlanForm
    template_name = "fleet/maintenance_plan_form.html"


    def form_valid(self, form):
        vehicle = Vehicle.objects.get(pk=self.kwargs["vehicle_pk"])
        form.instance.vehicle = vehicle
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = MaintenancePlan
    form_class = MaintenancePlanForm
    pk_url_kwarg = "maintenance_plan_pk"
    template_name = "fleet/maintenance_plan_form.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class MaintenancePlanDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = MaintenancePlan
    pk_url_kwarg = "maintenance_plan_pk"
    template_name = "fleet/maintenance_plan_confirm_delete.html"

    def get_success_url(self):
        pk = self.kwargs["vehicle_pk"]
        return reverse("fleet:vehicle-detail", kwargs={"pk": pk})


class ChangeTiresView(LoginRequiredMixin, generic.FormView):
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


class EmployeeListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.ListView
):
    model = CompanyUser
    context_object_name = "employee_list"
    template_name = "fleet/employee_list.html"
    paginate_by = 5

    def test_func(self):
        return self.request.user.is_owner

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_owner=False)


class EmployeeCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.CreateView
):
    form_class = EmployeeCreationForm
    template_name = "fleet/employee_form.html"
    success_url = reverse_lazy("fleet:employee-list")

    def test_func(self):
        return self.request.user.is_owner


class EmployeeUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    model = CompanyUser
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    template_name = "fleet/employee_form.html"
    success_url = reverse_lazy("fleet:employee-list")

    def test_func(self):
        return self.request.user.is_owner

    def get_queryset(self):
        return super().get_queryset().filter(is_owner=False)


class EmployeeStatusUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.View
):
    def test_func(self):
        return self.request.user.is_owner

    def post(self, request, pk):
        employee = CompanyUser.objects.get(
            pk=pk,
            is_owner=False
        )

        employee.is_active = not employee.is_active
        employee.save()

        return redirect("fleet:employee-list")


class VehicleMileageUpdateView(
    LoginRequiredMixin,
    generic.UpdateView
):
    model = Vehicle
    form_class = VehicleMileageUpdateForm
    template_name = "fleet/vehicle_mileage_form.html"

    def get_success_url(self):
        return reverse(
            "fleet:vehicle-detail",
            kwargs={"pk": self.object.pk}
        )



class TireSetListView(LoginRequiredMixin, generic.ListView):
    model = TireSet
    context_object_name = "tire_set_list"
    template_name = "fleet/tire_set_list.html"


class TireSetCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = TireSetForm
    template_name = "fleet/tire_set_form.html"
    success_url = reverse_lazy("fleet:tire-set-list")


class TireSetUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TireSet
    form_class = TireSetForm
    template_name = "fleet/tire_set_form.html"
    success_url = reverse_lazy("fleet:tire-set-list")


