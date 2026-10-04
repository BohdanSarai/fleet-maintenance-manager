from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from fleet.models import (
    CompanyUser,
    Vehicle,
    MaintenancePlan,
    ServiceRecord,
    TireSet,
    TireInstallation,
)


@admin.register(CompanyUser)
class CompanyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("is_owner",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": ("first_name", "last_name", "is_owner",)},
        ),
    )

admin.site.register(Vehicle)
admin.site.register(MaintenancePlan)
admin.site.register(ServiceRecord)
admin.site.register(TireSet)
admin.site.register(TireInstallation)
