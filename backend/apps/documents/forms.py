from django import forms
from .models import Insurance, CarteGrise, TechnicalInspection


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['vehicle', 'company_name', 'policy_number', 'start_date', 'end_date', 'premium_amount', 'is_active', 'document', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = user.vehicles.all()
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full text-sm text-gray-500'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
                field.widget.attrs['rows'] = 3
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'


class CarteGriseForm(forms.ModelForm):
    class Meta:
        model = CarteGrise
        fields = ['vehicle', 'registration_number', 'issue_date', 'expiry_date', 'document']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = user.vehicles.all()
        for field in self.fields.values():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full text-sm text-gray-500'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'


class TechnicalInspectionForm(forms.ModelForm):
    class Meta:
        model = TechnicalInspection
        fields = ['vehicle', 'inspection_date', 'result', 'expiry_date', 'mileage_at_inspection', 'garage_name', 'document', 'notes']
        widgets = {
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = user.vehicles.all()
        for field in self.fields.values():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full text-sm text-gray-500'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
                field.widget.attrs['rows'] = 3
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
