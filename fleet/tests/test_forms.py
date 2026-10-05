from django.core.exceptions import ValidationError
from django.test import TestCase

from fleet.forms import VehicleMileageUpdateForm
from fleet.models import Vehicle, TireSet, TireInstallation


class VehicleMileageUpdateFormTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

    def test_mileage_cannot_be_decreased(self):
        form = VehicleMileageUpdateForm(
            data={"current_mileage": 120000},
            instance=self.vehicle,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("current_mileage", form.errors)


class TireInstallationTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

        self.tire_set = TireSet.objects.create(
            season="winter",
            manufacturer="Continental",
            model="VikingContact",
            size="R16",
        )

    def test_removed_mileage_cannot_be_lower_than_installed_mileage(self):
        installation = TireInstallation(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=125000,
            removed_at_mileage=120000,
        )

        with self.assertRaises(ValidationError):
            installation.full_clean()

    def test_vehicle_cannot_have_two_active_tire_installations(self):
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=120000,
        )

        second_tire_set = TireSet.objects.create(
            season="summer",
            manufacturer="Michelin",
            model="Primacy",
            size="R16",
        )

        installation = TireInstallation(
            vehicle=self.vehicle,
            tire_set=second_tire_set,
            installed_at_mileage=130000,
        )

        with self.assertRaises(ValidationError):
            installation.full_clean()

    def test_tire_set_cannot_be_active_on_two_vehicles(self):
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=120000,
        )

        second_vehicle = Vehicle.objects.create(
            brand="Volkswagen",
            model="Passat",
            year=2016,
            license_plate="CE5678AA",
            fuel_type="diesel",
            current_mileage=150000,
        )

        installation = TireInstallation(
            vehicle=second_vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=150000,
        )

        with self.assertRaises(ValidationError):
            installation.full_clean()
