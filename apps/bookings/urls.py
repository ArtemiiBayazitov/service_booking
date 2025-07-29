from django.urls import path
from .views import SaunaDetailView, SaunaListView, OrderCreateView, PaymentView, OrderSuccessView


urlpatterns = [
    path('', SaunaListView.as_view(), name='saunas_list'),
    path('sauna/<int:pk>', SaunaDetailView.as_view(), name='sauna_detail'),
    path('sauna/order/', OrderCreateView.as_view(), name='order_create'),
    path('sauna/order/payment/<int:id>', PaymentView.as_view(), name='payment_page'),
    path('sauna/order/success/<int:pk>/', OrderSuccessView.as_view(), name='order_success'),
]