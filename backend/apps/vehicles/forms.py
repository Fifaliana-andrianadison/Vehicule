from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'name', 'brand', 'model', 'year', 'vehicle_type', 'fuel_type',
            'vin', 'registration_number', 'mileage', 'photo', 'purchase_date'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2030}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].widget.attrs['list'] = 'brand-datalist'
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
