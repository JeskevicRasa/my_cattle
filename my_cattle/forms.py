from django import forms
from my_farm.models import Cattle


class GenderForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = ['type', 'number', 'name', 'gender', 'breed', 'birth_date',
                  'entry_date', 'end_date', 'comments']
        widgets = {
            'gender': forms.Select(choices=Cattle.GENDER),
        }
