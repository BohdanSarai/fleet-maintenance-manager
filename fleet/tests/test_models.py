from django.core.exceptions import ValidationError
from django.test import TestCase

from fleet.models import TireInstallation, TireSet, Vehicle, MaintenancePlan, ServiceRecord, CompanyUser


class TireSetTests(TestCase):
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
            max_mileage=30000,
            initial_mileage=10000,
        )

    def test_tracked_mileage(self):
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=125000,
            removed_at_mileage=128000,
        )
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=128000,
            removed_at_mileage=130000,
        )

        self.assertEqual(
            self.tire_set.get_tracked_mileage(),
            5000,
        )

    def test_total_mileage(self):
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=125000,
            removed_at_mileage=130000,
        )

        self.assertEqual(
            self.tire_set.get_total_mileage(),
            15000,
        )

    def test_remaining_mileage(self):
        TireInstallation.objects.create(
            vehicle=self.vehicle,
            tire_set=self.tire_set,
            installed_at_mileage=125000,
            removed_at_mileage=130000,
        )

        self.assertEqual(
            self.tire_set.get_remaining_mileage(),
            15000,
        )

    def test_total_mileage_is_none_without_initial_mileage(self):
        self.tire_set.initial_mileage = None
        self.tire_set.save()

        self.assertIsNone(
            self.tire_set.get_total_mileage()
        )

    def test_remaining_mileage_is_none_without_max_mileage(self):
        self.tire_set.max_mileage = None
        self.tire_set.save()

        self.assertIsNone(
            self.tire_set.get_remaining_mileage()
        )


class MaintenancePlanTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

    def test_plan_requires_at_least_one_interval(self):
        plan = MaintenancePlan(
            vehicle=self.vehicle,
            name="Engine oil",
            mileage_interval=None,
            time_interval_months=None,
            start_mileage=130000,
        )

        with self.assertRaises(ValidationError):
            plan.full_clean()


class ServiceRecordTests(TestCase):
    def setUp(self):
        self.user = CompanyUser.objects.create_user(
            username="user",
            password="test12345",
        )

        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

    def test_service_mileage_cannot_exceed_vehicle_mileage(self):
        service_record = ServiceRecord(
            vehicle=self.vehicle,
            created_by=self.user,
            name="Engine oil replacement",
            date="2026-10-01",
            mileage=140000,
        )

        with self.assertRaises(ValidationError):
            service_record.full_clean()