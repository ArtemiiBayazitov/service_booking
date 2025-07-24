from datetime import timedelta
from django.db import models
from django.forms import ValidationError


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField(default=0.0)
    place = models.TextField()
    admin = models.TextField(max_length=255)
    extra_data = models.JSONField(default=dict, blank=True)


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
    

        


