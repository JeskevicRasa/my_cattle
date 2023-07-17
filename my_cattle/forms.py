from django import forms
from my_farm.models import Cattle, Herd, Field


class GenderForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = ['number', 'name', 'gender', 'breed', 'birth_date', 'acquisition_method',
                  'entry_date', 'loss_method', 'end_date', 'comments', 'picture']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.GENDER),
            'breed': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.BREED),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acquisition_method': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.ACQUISITION_METHOD),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loss_method': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.LOSS_METHOD),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class CattleForm(forms.ModelForm):
    herd = forms.ModelChoiceField(queryset=Herd.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Cattle
        fields = ['number', 'name', 'gender', 'breed', 'birth_date', 'acquisition_method',
                  'entry_date', 'loss_method', 'end_date', 'comments', 'picture', 'herd']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.GENDER),
            'breed': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.BREED),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acquisition_method': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.ACQUISITION_METHOD),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loss_method': forms.Select(attrs={'class': 'form-control'}, choices=Cattle.LOSS_METHOD),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class HerdForm(forms.ModelForm):
    cattle = forms.ModelMultipleChoiceField(queryset=Cattle.objects.all(), required=False)
    herd_leader = forms.ModelChoiceField(queryset=Cattle.objects.all(), required=False)

    class Meta:
        model = Herd
        fields = ['name', 'location', 'field', 'cattle', 'description', 'start_date', 'is_active', 'herd_leader', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'herd_leader': forms.Select(attrs={'class': 'form-control'}),
        }


class FieldForm(forms.ModelForm):
    herd = forms.ModelMultipleChoiceField(queryset=Herd.objects.all(), required=False)

    class Meta:
        model = Field
        fields = ['name', 'location', 'coordinates', 'field_size', 'size_unit', 'field_type', 'is_active',
                  'description', 'picture', 'herd']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
            'field_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'size_unit': forms.Select(attrs={'class': 'form-control'}),
            'field_type': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'herd': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }