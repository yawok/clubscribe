from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate, login, mixins, decorators, mixins
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, CreateView, ListView, DetailView
from . import forms, models
from django.http import HttpResponseRedirect
import logging
import os, uuid
from square.client import Client
from django.contrib import messages
from django.conf import settings
from django.template.defaultfilters import slugify
from .utils.square import Square

logger = logging.getLogger(__name__)

# client = Client(access_token=os.environ["SANDBOX_ACCESS_TOKEN"], environment="sandbox")

square_client = Square()

class CreateClubView(FormView):
    template_name = "create_club.html"
    form_class = forms.ClubForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        response = super().form_valid(form)
        form = form.save(commit=False)
        form.merchant_access_token = ...


@decorators.login_required
def authorize(request):
    """Requests merchant authorization"""
    if not request.user.is_merchant():
        authorization_redirect_url = square_client.get_authorization_url()
        context = {"url": authorization_redirect_url}
        return render(request, "authorize_merchant.html", context)
    messages.info(request, "You are already an authorised merchant")
    return HttpResponseRedirect(reverse("index"))


@decorators.login_required
def obtain_merchant_token(request):
    merchant_code = request.GET.get("code")
    merchant_token_info = square_client.obtain_merchant_token(merchant_code)
    
    if merchant_token_info: 
        merchant_square_client = Square(access_token=merchant_token_info.get("access_token"),)
        merchant_currency = merchant_square_client.get_merchant_currency()
        merchant_token_info["currency"] = merchant_currency
        merchant = models.Merchant.objects.create(**merchant_token_info)
        request.user.merchant = merchant
        request.user.save()
        messages.success(request, "Merchant account successfully linked")
        return HttpResponseRedirect(reverse('index'))
    messages.warning(request, "Merchant account link unsuccessful") 
    return HttpResponseRedirect(reverse('index'))


@decorators.login_required
def create_club(request):
    """Receives merchant authorization code and handles club creation with form"""
    if request.user.is_merchant():
        if request.method != "POST":
            form = forms.ClubForm()
        else:
            form = forms.ClubForm(request.POST)
            if form.is_valid():
                new_club = form.save(commit=False)
                club_name = form.cleaned_data['name']
                new_club.owner = request.user
                new_club.slug = slugify(club_name)
                new_club.save()
                logger.info(f"New club {new_club} has been created by {request.user}")
                return HttpResponseRedirect(reverse("club_detail", args=(new_club.slug,)))
        return render(request, "create_club.html", {"form": form})
    else:
        logger.info("Redirecting user to authorize Square account")
        return HttpResponseRedirect(reverse("authorize"))
        

class ClubDetailView(DetailView):
    model = models.Club
    template_name = "club_detail.html"
    context_object_name = "club"
    

def square_login(request):
    print
    # client = Client(
    #    access_token=os.environ["SANDBOX_ACCESS_TOKEN"], environment="sandbox"
    # )

    # result = client.o_auth.authorize(os.environ["SANDBOX_ACCESS_TOKEN"])

    # if result.is_success():
    # https://connect.squareup.com/oauth2/authorize?client_id={YOUR_APP_ID}&scope=CUSTOMERS_WRITE+CUSTOMERS_READ&session=false&state=82201dd8d83d23cc8a48caf52b
    #    context = {result.body}
    # elif result.is_error():
    #    context = {"error_code": "chaleeeeee!"}
    context = {"get": request.GET}
    return render(request, "locations.html", context)




@decorators.login_required
def create_subscription_catalog_item(request):
    merchant = request.user.merchant
    
    if request.user.is_merchant():
        merchant_square_client = Square(access_token=merchant.access_token)
        if request.method != "POST":
            form = forms.CreateSubscriptionForm(request.user)
        else:
            form = forms.CreateSubscriptionForm(request.user, data=request.POST)
            if form.is_valid():
                price = int(float(form.cleaned_data["price"]) * 100)
                subscription_arguments = form.cleaned_data
                subscription_arguments["converted_price"] = price
                subscription_arguments["currency"] = merchant.currency
                
                subscription_data = merchant_square_client.create_subscription_catalog_item(**subscription_arguments)
                
                if subscription_data:
                    subscription = models.SubscriptionPlan.objects.create(**subscription_data)
                    logger.info(f"{subscription_data.get('name')} Subscription created with id: {subscription_data.get('id')}")
                    return HttpResponseRedirect(reverse("subscriptions", args=(subscription_data.get("club").slug,)))
        return render(request, "create_subscription.html", {"form": form})
    return HttpResponseRedirect(reverse("authorize"))   


@decorators.login_required
def subscribe_to_club(request, pk):
    subscription_plan = get_object_or_404(models.SubscriptionPlan, pk=pk)
    plan_data = {
        "plan_name": subscription_plan.name,
        "price": subscription_plan.price,
        "currency": subscription_plan.club.owner.merchant.currency,
        "plan_id": subscription_plan.catalog_item_id
    }
    payment_url = square_client.create_payment_link(**plan_data)
    logger.info("Create payment link")
    context = {"plan": subscription_plan, "url": payment_url}
    return render(request, "subscribe_to_plan.html", context)
    return 
    
    

def join_club(request, slug):
    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email

    result = client.customers.create_customer(
        body = {
            "idempotency_key": f"{uuid.uuid4()}",
            "given_name":first_name,
            "family_name": last_name,
            "email_address": email,
        }
    )
    
    club = models.Club.objects.filter(slug=slug)
    user = request.user
    customer_id = result.body["customer"]["id"]
    models.objects.create(club=club, customer_id=customer_id, user=user)

class SubscriptionsListView(ListView):
    model = models.SubscriptionPlan
    paginate_by = 10
    template_name = "subscriptions_list.html"
    context_object_name = "subscriptions_list"
    
    def get_queryset(self):
        slug = self.kwargs['slug']
        club = models.Club.objects.get(slug=slug)
        subscriptions = get_list_or_404(models.SubscriptionPlan, club=club)
        return subscriptions


class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(f"New signup for {email} through SignupView.")
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You have signed up successfully.")

        return response


