import calendar
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


def add_months(source_date: date, months: int) -> date:
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(
        source_date.day,
        calendar.monthrange(year, month)[1],
    )
    return source_date.replace(
        year=year,
        month=month,
        day=day,
    )


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
    vin = models.CharField(
        max_length=17,
        unique=True,
        blank=True,
        null=True,
    )
    fuel_type = models.CharField(
        max_length=8,
        choices=FuelType.choices,
    )
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

    def get_absolute_url(self):
        return reverse(
            "fleet:vehicle-detail",
            args=[str(self.id)],
        )


class MaintenancePlan(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        related_name="maintenance_plans",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    mileage_interval = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    time_interval_months = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    start_mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    start_date = models.DateField(
        null=True,
        blank=True,
    )

    def clean(self):
        if not self.mileage_interval and not self.time_interval_months:
            raise ValidationError(
                "Specify mileage interval or time interval."
            )

    def __str__(self):
        return (
            f"{self.vehicle.brand} "
            f"{self.vehicle.model} - {self.name}"
        )

    def get_next_service_mileage(self):
        if self.mileage_interval is None:
            return None

        last_service = self.service_records.order_by(
            "-mileage"
        ).first()

        if last_service:
            base_mileage = last_service.mileage
        else:
            base_mileage = self.start_mileage

        if base_mileage is None:
            return None

        return base_mileage + self.mileage_interval

    def get_next_service_date(self):
        if self.time_interval_months is None:
            return None

        last_service = self.service_records.order_by(
            "-date"
        ).first()

        if last_service:
            base_date = last_service.date
        else:
            base_date = self.start_date

        if base_date is None:
            return None

        return add_months(
            base_date,
            self.time_interval_months,
        )


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
        related_name="service_records",
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    mileage = models.PositiveIntegerField()
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if (
            self.vehicle_id
            and self.mileage is not None
            and self.mileage > self.vehicle.current_mileage
        ):
            raise ValidationError("Update the car's mileage.")

        if (
            self.maintenance_plan_id
            and self.vehicle_id
            and self.maintenance_plan.vehicle_id != self.vehicle_id
        ):
            raise ValidationError(
                "The maintenance plan belongs to another vehicle."
            )

    def __str__(self):
        return (
            f"{self.vehicle.brand} {self.vehicle.model} - "
            f"{self.name} - {self.date}"
        )


class TireSet(models.Model):
    class Season(models.TextChoices):
        SUMMER = "summer", "for summer"
        WINTER = "winter", "for winter"
        ALL_SEASON = "all-season", "for all-season"

    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    size = models.CharField(max_length=10)
    season = models.CharField(
        max_length=10,
        choices=Season.choices,
    )
    max_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    initial_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    purchase_date = models.DateField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.manufacturer} {self.model} {self.size}"

    def get_tracked_mileage(self) -> int:
        mileage = 0

        for installation in self.tire_installations.all():
            if installation.removed_at_mileage is not None:
                mileage += (
                    installation.removed_at_mileage
                    - installation.installed_at_mileage
                )
            else:
                mileage += (
                    installation.vehicle.current_mileage
                    - installation.installed_at_mileage
                )

        return mileage

    def get_total_mileage(self) -> int | None:
        if self.initial_mileage is None:
            return None

        return (
            self.initial_mileage
            + self.get_tracked_mileage()
        )

    def get_remaining_mileage(self) -> int | None:
        total_mileage = self.get_total_mileage()

        if self.max_mileage is None or total_mileage is None:
            return None

        return self.max_mileage - total_mileage


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
    removed_at_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    def clean(self):
        if (
            self.removed_at_mileage is not None
            and self.removed_at_mileage
            < self.installed_at_mileage
        ):
            raise ValidationError(
                "Removed mileage cannot be less than "
                "installed mileage."
            )

        if (
            self.installed_at_mileage
            > self.vehicle.current_mileage
        ):
            raise ValidationError(
                "Installed mileage cannot be greater than "
                "current vehicle mileage."
            )

        if (
            self.removed_at_mileage is None
            and TireInstallation.objects.filter(
                vehicle=self.vehicle,
                removed_at_mileage__isnull=True,
            ).exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                "This vehicle already has an active tire set."
            )

        if (
            self.removed_at_mileage is None
            and TireInstallation.objects.filter(
                tire_set=self.tire_set,
                removed_at_mileage__isnull=True,
            ).exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                "This tire set is already installed "
                "on another vehicle."
            )

        if (
            self.removed_at_mileage is not None
            and self.removed_at_mileage
            > self.vehicle.current_mileage
        ):
            raise ValidationError(
                "Removed mileage cannot be greater than "
                "the vehicle's current mileage."
            )

    def __str__(self):
        return f"{self.vehicle} - {self.tire_set}"
