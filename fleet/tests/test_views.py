from django.test import TestCase
from django.urls import reverse

from fleet.models import CompanyUser, Vehicle, MaintenancePlan, ServiceRecord


class LoginRequiredTests(TestCase):
    def test_vehicle_list_requires_login(self):
        response = self.client.get(
            reverse("fleet:vehicle-list")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class EmployeeAccessTests(TestCase):
    def setUp(self):
        self.owner = CompanyUser.objects.create_user(
            username="owner",
            password="test12345",
            is_owner=True,
        )

        self.employee = CompanyUser.objects.create_user(
            username="employee",
            password="test12345",
            is_owner=False,
        )

    def test_owner_can_access_employee_list(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("fleet:employee-list")
        )

        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_employee_list(self):
        self.client.force_login(self.employee)

        response = self.client.get(
            reverse("fleet:employee-list")
        )

        self.assertEqual(response.status_code, 403)


class VehicleSearchTests(TestCase):
    def setUp(self):
        self.user = CompanyUser.objects.create_user(
            username="user",
            password="test12345",
        )
        self.client.force_login(self.user)

        Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

        Vehicle.objects.create(
            brand="Volkswagen",
            model="Passat",
            year=2016,
            license_plate="CE5678AA",
            fuel_type="diesel",
            current_mileage=150000,
        )

    def test_search_vehicle_by_brand(self):
        response = self.client.get(
            reverse("fleet:vehicle-list"),
            {"query": "Ford"},
        )

        self.assertContains(response, "Mondeo")
        self.assertNotContains(response, "Passat")


class MaintenancePlanSearchTests(TestCase):
    def setUp(self):
        self.user = CompanyUser.objects.create_user(
            username="user",
            password="test12345",
        )
        self.client.force_login(self.user)

        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

        MaintenancePlan.objects.create(
            vehicle=self.vehicle,
            name="Engine oil",
            mileage_interval=10000,
            start_mileage=120000,
        )

        MaintenancePlan.objects.create(
            vehicle=self.vehicle,
            name="Brake fluid",
            time_interval_months=24,
            start_mileage=120000,
        )

    def test_search_maintenance_plan_by_name(self):
        response = self.client.get(
            reverse("fleet:maintenance-plan-list"),
            {"query": "Engine"},
        )

        self.assertContains(response, "Engine oil")
        self.assertNotContains(response, "Brake fluid")


class ServiceRecordSearchTests(TestCase):
    def setUp(self):
        self.user = CompanyUser.objects.create_user(
            username="user",
            password="test12345",
        )
        self.client.force_login(self.user)

        self.vehicle = Vehicle.objects.create(
            brand="Ford",
            model="Mondeo",
            year=2015,
            license_plate="CE1234AA",
            fuel_type="petrol",
            current_mileage=130000,
        )

        ServiceRecord.objects.create(
            vehicle=self.vehicle,
            created_by=self.user,
            name="Engine oil replacement",
            date="2026-10-01",
            mileage=129000,
        )

        ServiceRecord.objects.create(
            vehicle=self.vehicle,
            created_by=self.user,
            name="Brake repair",
            date="2026-09-01",
            mileage=125000,
        )

    def test_search_service_record_by_name(self):
        response = self.client.get(
            reverse("fleet:service-record-list"),
            {"query": "Engine"},
        )

        self.assertContains(response, "Engine oil replacement")
        self.assertNotContains(response, "Brake repair")
