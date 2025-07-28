from django import forms
from .models import Order
from django.core.exceptions import ValidationError
from django.utils import timezone


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name_client', 'contact_client', 'time_start', 'time_end', 'service']
        widgets = {
            'time_start': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'time_end': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'full_name_client': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_client': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'full_name_client': 'ФИО клиента',
            'contact_client': 'Контактный телефон',
            'time_start': 'Начало бронирования',
            'time_end': 'Окончание бронирования',
            'service': 'Сауна / Услуга',
        }

    def clean_time_start(self):
        time_start = self.cleaned_data['time_start']
        if time_start < timezone.now():
            raise ValidationError("Нельзя бронировать на прошлое время.")
        return time_start
    
    