from django import forms
from django.contrib.auth.forms import UserCreationForm

from fleet.models import TireSet, CompanyUser


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
        label=""
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

