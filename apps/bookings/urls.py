from django.urls import path
from .views import SaunaDetailView, SaunaListView, OrderCreateView


urlpatterns = [
    path('', SaunaListView.as_view(), name='saunas_list'),
    path('sauna/<int:pk>', SaunaDetailView.as_view(), name='sauna_detail'),
    path('order/create/', OrderCreateView.as_view(), name='order_create')
]