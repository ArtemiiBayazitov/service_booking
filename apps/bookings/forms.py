from django import forms
from .models import Order
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class OrderForm(forms.ModelForm):
    duration = forms.ChoiceField(
        label='Длительность в часах',
        choices=[(i, f"{i} ч.") for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Order
        fields = ['full_name_client', 'email_client', 'contact_client', 'time_start', 'service']
        widgets = {
            'time_start': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'full_name_client': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_client': forms.TextInput(attrs={'class': 'form-control'}),
            'email_client': forms.EmailInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'full_name_client': 'ФИО клиента',
            'contact_client': 'Контактный телефон',
            'time_start': 'Начало бронирования',
            'time_end': 'Окончание бронирования',
            'email_client': 'EMAIL для подтверждения бронирования',
            'service': 'Сауна / Услуга',
        }

    def clean_time_start(self):
        time_start = self.cleaned_data['time_start']
        if time_start < timezone.now():
            raise ValidationError("Нельзя бронировать на прошлое время.")
        return time_start
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        duration = int(self.cleaned_data['duration_hours'])
        instance.time_end = instance.time_start + timedelta(hours=duration)
        instance.total_price = instance.total_price_count

        if commit:
            instance.save()
        return instance


