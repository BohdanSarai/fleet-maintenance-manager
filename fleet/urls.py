from  django.urls import path
from fleet.views import (
    IndexView,
    VehicleListView,
    VehicleDetailView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
]


app_name = "fleet"