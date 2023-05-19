from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, ListView
from . import forms, models
import logging
import os, uuid
from square.client import Client

logger = logging.getLogger(__name__)

client = Client(
        access_token=os.environ["SANDBOX_ACCESS_TOKEN"], environment="sandbox"
    )

class CreateClubView(FormView):
    template_name = "create_club.html"
    form_class = forms.ClubForm
    success_url = reverse_lazy("index")


def square_login(request):
    client = Client(
        access_token=os.environ["SANDBOX_ACCESS_TOKEN"], environment="sandbox"
    )

    result = client.o_auth.retrieve_token_status(os.environ["SANDBOX_ACCESS_TOKEN"])

    if result.is_success():
        context = {result.body}
    elif result.is_error():
        context = {"error_code": "chaleeeeee!"}

    return render(request, "locations.html", context)


def create_subscription(request):
    if request.method != "POST":
        form = forms.CreateSubscriptionForm()
    else:
        form = forms.CreateSubscriptionForm(data=request.POST)
        if form.is_valid():
            amount = int(form.cleaned_data["amount"]) * 100
            result = client.catalog.upsert_catalog_object(
                body={
                    "idempotency_key": f"{uuid.uuid4()}",
                    "object": {
                        "type": "SUBSCRIPTION_PLAN",
                        "id": "#1",
                        "subscription_plan_data": {
                            "name": f"{form.cleaned_data['name']}",
                            "phases": [
                                {
                                    "cadence": f"{form.cleaned_data['period']}",
                                    "periods": 1,
                                    "recurring_price_money": {
                                        "amount": amount,
                                        "currency": "USD",
                                    },
                                    "ordinal": 1,
                                }
                            ],
                        },
                    },
                }
            )


        if result.is_success():
            id = result.body["catalog_object"]["id"]
            name = result.body["catalog_object"]["subscription_plan_data"]["name"]
            subscription = models.SubscriptionPlan.objects.create(subscription_id=id, name=name)
            logger.info(f"{name} Subscription created with id: {id}")
            return render(request, "subscription_details.html", {"subscription": subscription})
            
        elif result.is_error():
            print(result.errors)
        
    return render(request, "create_subscription.html", {"form": form})


class SubscriptionsListView(ListView):
    model = models.SubscriptionPlan
    paginate_by = 10
    template_name = "subscriptions_list.html"
    context_object_name = "subscriptions_list"