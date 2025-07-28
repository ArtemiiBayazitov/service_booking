from datetime import timedelta
from django.db import models
from django.forms import ValidationError


class Service(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, blank=True)
    price = models.FloatField(default=0.0)
    place = models.TextField()
    admin = models.TextField(max_length=255)
    extra_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"      
        CONFIRMED = "confirmed", "Подтверждено" 
        PREDPAID = 'prepaid', 'Предоплата внесена'          
        PAID = "paid", "Оплачено"                         
        IN_PROGRESS = "in_progress", "В процессе"         
        COMPLETED = "completed", "Завершено"              
        CANCELED = "canceled", "Отменено"                 
        REFUNDED = "refunded", "Возврат средств"          

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    full_name_client = models.CharField(max_length=255)
    contact_client = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    extra_data = models.JSONField(default=dict, blank=True)
    total_price = models.FloatField(default=0)
    
    @property
    def total_price_count(self):
        price_per_hour = self.service.price
        total_time = self.duration.total_seconds() / 3600
        return round(price_per_hour * total_time, 2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.total_price_count
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if self.time_end <= self.time_start:
            raise ValidationError('Время окончания должно быть позже начала')
        
    @property
    def duration(self) -> timedelta:
        data = self.time_end - self.time_start
        return data
        
    @property
    def is_active(self) -> bool:
        return self.status in {self.Status.PAID, self.Status.IN_PROGRESS}
    
    def __str__(self) -> str:
        return f'Заказ {self.pk}, статус: {self.get_status_display()}'
    

        


