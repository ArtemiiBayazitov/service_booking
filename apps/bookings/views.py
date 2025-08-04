from django.core.cache import cache
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.contrib import messages
from .models import Service, Order
from .forms import OrderForm
from django.views.generic import ListView, DetailView
import random
from datetime import timedelta, datetime

CACHES_ORDER_ID = []


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
    template_name = 'order_create.html'  
    success_url = 'payment/'

    def form_valid(self, form) -> HttpResponse:
        global CACHES_ORDER_ID
        order_id = random.randint(1000000, 9999999)
        while cache.get(f'order:{order_id}'):
            order_id = random.randint(1000000, 9999999)

        cleaned_data = form.cleaned_data.copy()
        cleaned_data['service'] = form.cleaned_data['service'].id
        duration = int(form.cleaned_data['duration'])
        time_start = form.cleaned_data['time_start']
        time_end = time_start + timedelta(hours=duration)
        cleaned_data['time_end'] = time_end 
        cache.set(f'order:{order_id}', cleaned_data, timeout=600)
        CACHES_ORDER_ID.append(order_id)
        print(f'id from form valid: {order_id}')

        return redirect('payment_page', id=order_id)
    
    def get_initial(self):
        initial = super().get_initial()
        sauna_id = self.request.GET.get('sauna')
        if sauna_id:
            initial['service'] = sauna_id
        return initial
    

class PaymentView(TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('id')
        order_data = cache.get(f'order:{order_id}')

        if not order_data:
            raise Http404("Заказ не найден или устарел.")

        try:
            service = Service.objects.get(pk=order_data['service'])
        except Service.DoesNotExist:
            raise Http404("Услуга не найдена.")
        
        start = order_data['time_start']
        end = order_data['time_end']
        duration_hours = (end - start).total_seconds() / 3600
        price_per_hour = service.price
        total_price = round(price_per_hour * duration_hours, 2)

        context.update({
            'order_id': order_id,
            'order_data': order_data,
            'service': service,
            'price_per_hour': price_per_hour,
            'duration_hours': duration_hours,
            'total_price': total_price,
        })

        return context
    
    def post(self, request, id) -> HttpResponseNotFound | HttpResponseRedirect | None:
        action = request.POST.get('action')
        key = f'order:{id}'
        order_data = cache.get(key)

        if not order_data:
            return HttpResponseNotFound('Заказ не найден или устарел')
        
        if action in {'prepaid', 'paid'}:
            try:
                service = Service.objects.get(pk=order_data['service'])
            except Service.DoesNotExist:
                return HttpResponseNotFound('Услуга не найдена ')

            order = Order.objects.create(
                status=Order.Status.PREDPAID if action == 'prepaid' else Order.Status.PAID,
                time_start=order_data['time_start'],
                time_end=order_data['time_end'],
                full_name_client=order_data['full_name_client'],
                contact_client=order_data['contact_client'],
                email_client=order_data.get('email_client', ''),
                service=service,
                extra_data={},
            )

            cache.delete(key)

            return HttpResponseRedirect(reverse('order_success', args=[order.pk]))
        
        elif action == 'cancel':
            messages.info(request, "Оплата отменена.")
            return self.get(request, id)

        messages.error(request, "Неизвестное действие.")
        return self.get(request, id)
    

class OrderSuccessView(DetailView):
    model = Order
    template_name = 'order_success.html'
    context_object_name = 'order'
    

def get_busy_times(request) -> JsonResponse:
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        sauna_id = request.GET.get('sauna')
        time_start = request.GET.get('time_start')
        try:
            selected_date = datetime.strptime(time_start, '%Y-%m-%dT%H:%M')
            busy_orders = Order.objects.filter(
                service=sauna_id,
                time_start__date=selected_date.date(),
                status__in=[Order.Status.PAID, Order.Status.PREDPAID, Order.Status.IN_PROGRESS]
            ).values('time_start', 'time_end')
            busy_times = [
                f"{order['time_start'].strftime('%H:%M')} - {order['time_end'].strftime('%H:%M')}"
                for order in busy_orders
            ]
            print(CACHES_ORDER_ID)
            
            for key in CACHES_ORDER_ID:
                order_data = cache.get(f'order:{key}')
                if order_data and str(order_data.get('service')) == str(sauna_id):
                    cache_time_start = order_data.get('time_start')
                    if cache_time_start.date() == selected_date.date():
                        cache_time_end = order_data.get('time_end')
                        busy_times.append(
                            f"{cache_time_start.strftime('%H:%M')} - {cache_time_end.strftime('%H:%M')}"
                        )
            return JsonResponse({'busy_times': busy_times})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Неверный формат даты или сауны'}, status=400)
    return JsonResponse({'error': 'Не AJAX-запрос'}, status=400)
