from django import forms

from fleet.models import TireSet


class ChangeTiresForm(forms.Form):
    tire_set = forms.ModelChoiceField(
        queryset=TireSet.objects.none()
    )

    def __init__(self, *args, tire_sets=None, **kwargs):
        super().__init__(*args, **kwargs)

        if tire_sets is not None:
            self.fields["tire_set"].queryset = tire_sets


