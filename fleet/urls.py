from  django.urls import path
from django.views import View

from fleet.views import (
    IndexView,
    VehicleListView,
    VehicleDetailView,
    VehicleCreateView,
    VehicleUpdateView,
    VehicleDeleteView,
    ServiceRecordCreateView,
    ServiceRecordUpdateView,
    ServiceRecordDeleteView,
    MaintenancePlanCreateView,
    MaintenancePlanUpdateView,
    MaintenancePlanDeleteView,
    TireInstallationCreateView,
    ChangeTiresView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
    path("vehicles/create/", VehicleCreateView.as_view(), name="vehicle-create"),
    path("vehicles/<int:pk>/update/", VehicleUpdateView.as_view(), name="vehicle-update"),
    path("vehicles/<int:pk>/delete/", VehicleDeleteView.as_view(), name="vehicle-delete"),
    path("vehicles/<int:pk>/service-records/create/", ServiceRecordCreateView.as_view(), name="vehicle-service-record-create"),
    path("vehicles/<int:vehicle_pk>/service-record/<int:service_record_pk>/update/", ServiceRecordUpdateView.as_view(), name="vehicle-service-record-update"),
    path("vehicles/<int:vehicle_pk>/service-record/<int:service_record_pk>/delete/", ServiceRecordDeleteView.as_view(), name="vehicle-service-record-delete"),
    path("vehicles/<int:vehicle_pk>/maintenance-plan/create/", MaintenancePlanCreateView.as_view(), name="vehicle-maintenance-plan-create"),
    path("vehicles/<int:vehicle_pk>/maintenance-plan/<int:maintenance_plan_pk>/update/", MaintenancePlanUpdateView.as_view(), name="vehicle-maintenance-plan-update"),
    path("vehicles/<int:vehicle_pk>/maintenance-plan/<int:maintenance_plan_pk>/delete/", MaintenancePlanDeleteView.as_view(),
         name="vehicle-maintenance-plan-delete"),
    path("vehicles/<int:vehicle_pk>/tire-installations/create/", TireInstallationCreateView.as_view(), name="vehicle-tire-installation-create"),
    path(
        "vehicles/<int:vehicle_pk>/change-tires/",
        ChangeTiresView.as_view(),
        name="vehicle-change-tires",
    ),
]


app_name = "fleet"