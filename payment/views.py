import json
from django.http import HttpResponse
import stripe

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.generic.base import TemplateView

import os

from cart.cart import Cart
from orders.views import payment_confirmation


def order_placed(request):
    cart = Cart(request)
    cart.clear()
    return render(request, 'payment/orderplaced.html')

class Error(TemplateView):
    template_name = 'payment/error.html'

@login_required
def CartView(request):
    
    cart = Cart(request)
    total = str(cart.get_total_price())
    # Strip doesn't do decimals, 1099 == 10.99 on Stripe
    total = total.replace('.', '')
    total = int(total)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount = total,
        currency = 'usd',
        metadata = {'userid': request.user.id}
    )

    return render(request, 'payment/payment_form.html', {'client_secret': intent.client_secret, 'STRIPE_PUBLISHABLE_KEY': os.environ.get("STRIPE_PUBLISHABLE_KEY")})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try: 
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)

    if event.type == 'payment_intent.succeeded':
        payment_confirmation(event.data.object.client_secret)

    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)

