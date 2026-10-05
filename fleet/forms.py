from django import forms
from django.contrib.auth.forms import UserCreationForm

from fleet.models import TireSet, CompanyUser, Vehicle, MaintenancePlan, ServiceRecord


class ChangeTiresForm(forms.Form):
    tire_set = forms.ModelChoiceField(
        queryset=TireSet.objects.none()
    )

    def __init__(self, *args, tire_sets=None, **kwargs):
        super().__init__(*args, **kwargs)

        if tire_sets is not None:
            self.fields["tire_set"].queryset = tire_sets


class VehicleSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by brand, model or license plate",
            }
        ),
    )


class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CompanyUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class VehicleMileageUpdateForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ("current_mileage",)
        labels = {
            "current_mileage": "New mileage",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_mileage = self.instance.current_mileage

    def clean_current_mileage(self):
        new_mileage = self.cleaned_data["current_mileage"]

        if new_mileage < self.previous_mileage:
            raise forms.ValidationError(
                "Mileage cannot be lower than the current mileage."
            )

        return new_mileage


class MaintenancePlanForm(forms.ModelForm):
    class Meta:
        model = MaintenancePlan
        fields = (
            "name",
            "description",
            "mileage_interval",
            "time_interval_months",
            "start_mileage",
            "start_date",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = (
            "maintenance_plan",
            "name",
            "date",
            "mileage",
            "cost",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class TireSetForm(forms.ModelForm):
    class Meta:
        model = TireSet
        fields = (
            "season",
            "manufacturer",
            "model",
            "size",
            "max_mileage",
            "initial_mileage",
            "purchase_date",
        )
        widgets = {
            "purchase_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }


class MaintenancePlanSearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search maintenance plans",
            }
        ),
    )


class ServiceRecordSearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search service history",
            }
        ),
    )

