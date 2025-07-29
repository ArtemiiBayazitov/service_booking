from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Service, Order
from .forms import OrderForm
from django.views.generic import ListView, DetailView


class SaunaListView(ListView):
    model = Service
    template_name = 'saunas_list.html'
    context_object_name = 'saunas'


class SaunaDetailView(DetailView):
    model = Service
    template_name = 'sauna_detail.html'
    context_object_name = 'sauna'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_create.html'  # создашь шаблон
    success_url = 'payment/'  # перенаправление после успешной отправки

    def form_valid(self, form) -> HttpResponse:
        # здесь можно пересчитать цену, extra_data, и т.д.
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        sauna_id = self.request.GET.get('sauna')
        if sauna_id:
            initial['service'] = sauna_id
        return initial
    

class PaymentView(TemplateView):
    template_name = 'payment.html'
    

    

