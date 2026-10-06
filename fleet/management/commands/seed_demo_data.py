from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from fleet.models import (
    CompanyUser,
    MaintenancePlan,
    ServiceRecord,
    TireInstallation,
    TireSet,
    Vehicle,
)


DEMO_PASSWORD = "FleetDemo2026!"


class Command(BaseCommand):
    help = "Create demo data for Fleet Maintenance Manager"  # noqa: VNE003

    def handle(self, *args, **options):
        owner, _ = CompanyUser.objects.get_or_create(
            username="demo.owner",
            defaults={
                "first_name": "Demo",
                "last_name": "Owner",
                "email": "owner@example.com",
                "is_owner": True,
            },
        )
        owner.is_owner = True
        owner.is_staff = False
        owner.is_superuser = False
        owner.set_password(DEMO_PASSWORD)
        owner.save()

        employee, _ = CompanyUser.objects.get_or_create(
            username="demo.employee",
            defaults={
                "first_name": "Demo",
                "last_name": "Employee",
                "email": "employee@example.com",
                "is_owner": False,
            },
        )
        employee.is_owner = False
        employee.is_staff = False
        employee.is_superuser = False
        employee.set_password(DEMO_PASSWORD)
        employee.save()

        transit, _ = Vehicle.objects.get_or_create(
            license_plate="CE1234AB",
            defaults={
                "brand": "Ford",
                "model": "Transit",
                "year": 2021,
                "vin": "WF0XXXTTGXMA12345",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 124500,
            },
        )

        caddy, _ = Vehicle.objects.get_or_create(
            license_plate="CE5678BC",
            defaults={
                "brand": "Volkswagen",
                "model": "Caddy",
                "year": 2020,
                "vin": "WV1ZZZ2KZLX123456",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 89500,
            },
        )

        corolla, _ = Vehicle.objects.get_or_create(
            license_plate="CE9012CA",
            defaults={
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2022,
                "vin": "JTDBR32E720123456",
                "fuel_type": Vehicle.FuelType.HYBRID,
                "current_mileage": 47200,
            },
        )

        leaf, _ = Vehicle.objects.get_or_create(
            license_plate="CE3456DE",
            defaults={
                "brand": "Nissan",
                "model": "Leaf",
                "year": 2021,
                "vin": "SJNFAAZE1U0123456",
                "fuel_type": Vehicle.FuelType.ELECTRIC,
                "current_mileage": 61300,
            },
        )

        master, _ = Vehicle.objects.get_or_create(
            license_plate="CE7890EA",
            defaults={
                "brand": "Renault",
                "model": "Master",
                "year": 2018,
                "vin": "VF1MA000X60123456",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 186400,
                "is_active": False,
            },
        )

        transit_oil, _ = MaintenancePlan.objects.get_or_create(
            vehicle=transit,
            name="Engine oil and filter",
            defaults={
                "description": "Replace engine oil and oil filter.",
                "mileage_interval": 10000,
                "time_interval_months": 12,
                "start_mileage": 100000,
                "start_date": date(2025, 1, 15),
            },
        )

        transit_air, _ = MaintenancePlan.objects.get_or_create(
            vehicle=transit,
            name="Air filter",
            defaults={
                "mileage_interval": 20000,
                "start_mileage": 100000,
            },
        )

        transit_brakes, _ = MaintenancePlan.objects.get_or_create(
            vehicle=transit,
            name="Brake inspection",
            defaults={
                "mileage_interval": 15000,
                "time_interval_months": 12,
                "start_mileage": 100000,
                "start_date": date(2025, 3, 1),
            },
        )

        caddy_oil, _ = MaintenancePlan.objects.get_or_create(
            vehicle=caddy,
            name="Engine oil and filter",
            defaults={
                "mileage_interval": 10000,
                "time_interval_months": 12,
                "start_mileage": 70000,
                "start_date": date(2025, 2, 10),
            },
        )

        caddy_timing, _ = MaintenancePlan.objects.get_or_create(
            vehicle=caddy,
            name="Timing belt",
            defaults={
                "mileage_interval": 60000,
                "start_mileage": 60000,
            },
        )

        corolla_oil, _ = MaintenancePlan.objects.get_or_create(
            vehicle=corolla,
            name="Engine oil and filter",
            defaults={
                "mileage_interval": 10000,
                "time_interval_months": 12,
                "start_mileage": 30000,
                "start_date": date(2025, 4, 5),
            },
        )

        corolla_brake_fluid, _ = MaintenancePlan.objects.get_or_create(
            vehicle=corolla,
            name="Brake fluid",
            defaults={
                "time_interval_months": 24,
                "start_date": date(2024, 6, 1),
            },
        )

        leaf_inspection, _ = MaintenancePlan.objects.get_or_create(
            vehicle=leaf,
            name="General EV inspection",
            defaults={
                "mileage_interval": 15000,
                "time_interval_months": 12,
                "start_mileage": 45000,
                "start_date": date(2025, 5, 1),
            },
        )

        leaf_filter, _ = MaintenancePlan.objects.get_or_create(
            vehicle=leaf,
            name="Cabin air filter",
            defaults={
                "mileage_interval": 20000,
                "time_interval_months": 12,
                "start_mileage": 40000,
                "start_date": date(2025, 5, 1),
            },
        )

        service_records = [
            (
                transit,
                transit_oil,
                owner,
                "Engine oil and filter",
                date(2026, 3, 10),
                115000,
                Decimal("180.00"),
            ),
            (
                transit,
                transit_air,
                employee,
                "Air filter replacement",
                date(2026, 2, 18),
                110000,
                Decimal("45.00"),
            ),
            (
                transit,
                transit_brakes,
                employee,
                "Brake inspection",
                date(2026, 1, 20),
                108000,
                Decimal("60.00"),
            ),
            (
                caddy,
                caddy_oil,
                owner,
                "Engine oil and filter",
                date(2026, 4, 2),
                85000,
                Decimal("160.00"),
            ),
            (
                caddy,
                caddy_timing,
                employee,
                "Timing belt inspection",
                date(2026, 1, 12),
                80000,
                Decimal("90.00"),
            ),
            (
                corolla,
                corolla_oil,
                employee,
                "Engine oil and filter",
                date(2026, 5, 5),
                45000,
                Decimal("140.00"),
            ),
            (
                corolla,
                corolla_brake_fluid,
                owner,
                "Brake fluid replacement",
                date(2026, 4, 14),
                43500,
                Decimal("75.00"),
            ),
            (
                leaf,
                leaf_inspection,
                owner,
                "General EV inspection",
                date(2026, 4, 25),
                58000,
                Decimal("120.00"),
            ),
            (
                leaf,
                leaf_filter,
                employee,
                "Cabin air filter",
                date(2026, 3, 17),
                55000,
                Decimal("40.00"),
            ),
        ]

        for (
            vehicle,
            maintenance_plan,
            created_by,
            name,
            service_date,
            mileage,
            cost,
        ) in service_records:
            ServiceRecord.objects.get_or_create(
                vehicle=vehicle,
                maintenance_plan=maintenance_plan,
                name=name,
                date=service_date,
                mileage=mileage,
                defaults={
                    "created_by": created_by,
                    "cost": cost,
                },
            )

        transit_winter, _ = TireSet.objects.get_or_create(
            manufacturer="Continental",
            model="VanContact Winter",
            size="215/65R16",
            defaults={
                "season": TireSet.Season.WINTER,
                "max_mileage": 60000,
                "initial_mileage": 0,
                "purchase_date": date(2024, 11, 1),
            },
        )

        transit_summer, _ = TireSet.objects.get_or_create(
            manufacturer="Michelin",
            model="Agilis 3",
            size="215/65R16",
            defaults={
                "season": TireSet.Season.SUMMER,
                "max_mileage": 70000,
                "initial_mileage": 5000,
                "purchase_date": date(2025, 4, 1),
            },
        )

        caddy_summer, _ = TireSet.objects.get_or_create(
            manufacturer="Goodyear",
            model="EfficientGrip",
            size="205/55R16",
            defaults={
                "season": TireSet.Season.SUMMER,
                "max_mileage": 60000,
                "initial_mileage": 0,
                "purchase_date": date(2025, 3, 20),
            },
        )

        caddy_winter, _ = TireSet.objects.get_or_create(
            manufacturer="Continental",
            model="WinterContact",
            size="205/55R16",
            defaults={
                "season": TireSet.Season.WINTER,
                "max_mileage": 55000,
                "initial_mileage": 3000,
                "purchase_date": date(2024, 10, 15),
            },
        )

        corolla_summer, _ = TireSet.objects.get_or_create(
            manufacturer="Bridgestone",
            model="Turanza 6",
            size="205/55R16",
            defaults={
                "season": TireSet.Season.SUMMER,
                "max_mileage": 65000,
                "initial_mileage": 0,
                "purchase_date": date(2025, 4, 10),
            },
        )

        leaf_all_season, _ = TireSet.objects.get_or_create(
            manufacturer="Michelin",
            model="CrossClimate 2",
            size="215/50R17",
            defaults={
                "season": TireSet.Season.ALL_SEASON,
                "max_mileage": 65000,
                "initial_mileage": 0,
                "purchase_date": date(2025, 2, 1),
            },
        )

        installations = [
            (transit, transit_winter, 100000, 112000),
            (transit, transit_summer, 112000, None),
            (caddy, caddy_winter, 70000, 81000),
            (caddy, caddy_summer, 81000, None),
            (corolla, corolla_summer, 35000, None),
            (leaf, leaf_all_season, 45000, None),
        ]

        for (
            vehicle,
            tire_set,
            installed_at,
            removed_at,
        ) in installations:
            TireInstallation.objects.get_or_create(
                vehicle=vehicle,
                tire_set=tire_set,
                installed_at_mileage=installed_at,
                defaults={
                    "removed_at_mileage": removed_at,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data created successfully."
            )
        )
