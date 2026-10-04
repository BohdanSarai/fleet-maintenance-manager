from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CompanyUser(AbstractUser):
    is_owner = models.BooleanField(default=False)


class Vehicle(models.Model):
    class FuelType(models.TextChoices):
        PETROL = "petrol", "petrol engine"
        DIESEL = "diesel", "diesel engine"
        GAS = "gas", "gas engine"
        HYBRID = "hybrid", "hybrid engine"
        ELECTRIC = "electric", "electric engine"

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=10, unique=True)
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True)
    fuel_type = models.CharField(max_length=8, choices=FuelType.choices)
    current_mileage = models.PositiveIntegerField()
    tire_sets = models.ManyToManyField(
        "TireSet",
        through="TireInstallation",
        related_name="vehicles",
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class MaintenancePlan(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        related_name="maintenance_plans",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    mileage_interval = models.PositiveIntegerField(blank=True, null=True)
    time_interval_months = models.PositiveIntegerField(blank=True, null=True)

    def clean(self):
        if not self.mileage_interval and not self.time_interval_months:
            raise ValidationError("Specify mileage interval or time interval.")

    def __str__(self):
        return f"{self.vehicle.brand} {self.vehicle.model} - {self.name}"


class ServiceRecord(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="service_records",
    )
    maintenance_plan = models.ForeignKey(
        MaintenancePlan,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_records",
    )
    created_by = models.ForeignKey(
        CompanyUser,
        on_delete=models.PROTECT,
        related_name="service_records"
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    mileage = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.mileage > self.vehicle.current_mileage:
            raise ValidationError("Update the car's mileage.")
        if self.maintenance_plan and self.maintenance_plan.vehicle != self.vehicle:
            raise ValidationError("The maintenance plan belongs to another vehicle.")

    def __str__(self):
        return f"{self.vehicle.brand} {self.vehicle.model} - {self.name} - {self.date}"


class TireSet(models.Model):
    class Season(models.TextChoices):
        SUMMER = "summer", "for summer"
        WINTER = "winter", "for winter"
        ALL_SEASON = "all-season", "for all-season"

    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    size = models.CharField(max_length=10)
    season = models.CharField(max_length=10, choices=Season.choices)
    max_mileage = models.PositiveIntegerField(blank=True, null=True)
    initial_mileage = models.PositiveIntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model} {self.size}"


class TireInstallation(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="tire_installations",
    )
    tire_set = models.ForeignKey(
        TireSet,
        on_delete=models.PROTECT,
        related_name="tire_installations",
    )
    installed_at_mileage = models.PositiveIntegerField()
    removed_at_mileage = models.PositiveIntegerField(blank=True, null=True)

    def clean(self):
        if self.removed_at_mileage is not None and self.removed_at_mileage < self.installed_at_mileage:
            raise ValidationError("Removed mileage cannot be less than installed mileage.")
        if self.installed_at_mileage > self.vehicle.current_mileage:
            raise ValidationError("Installed mileage cannot be greater than current vehicle mileage.")
        if (
            self.removed_at_mileage is None
            and TireInstallation.objects.filter(
                vehicle=self.vehicle,
                removed_at_mileage__isnull=True
            ).exclude(pk=self.pk).exists()
        ):
            raise ValidationError("This vehicle already has an active tire set.")
        if (
            self.removed_at_mileage is None
            and TireInstallation.objects.filter(
                tire_set=self.tire_set,
                removed_at_mileage__isnull=True
            ).exclude(pk=self.pk).exists()
        ):
            raise ValidationError("This tire set is already installed on another vehicle.")
        if self.removed_at_mileage is not None and self.removed_at_mileage > self.vehicle.current_mileage:
            raise ValidationError("Removed mileage cannot be greater than the vehicle's current mileage.")

    def __str__(self):
        return f"{self.vehicle} - {self.tire_set}"

