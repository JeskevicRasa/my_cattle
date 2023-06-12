from django import forms
from my_farm.models import Cattle


class GenderForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = ['type', 'number', 'name', 'gender', 'breed', 'birth_date', 'acquisition_method',
                  'entry_date', 'loss_method', 'end_date', 'comments']
        widgets = {
            'gender': forms.Select(choices=Cattle.GENDER),
            'acquisition_method': forms.Select(choices=Cattle.ACQUISITION_METHOD),
            'loss_method': forms.Select(choices=Cattle.LOSS_METHOD),
        }


class CattleForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = '__all__'
