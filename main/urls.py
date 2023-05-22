from django.urls import path, include
from django.views.generic import TemplateView, DetailView, ListView
from . import views, models

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("create_club/", views.create_club, name="create_club"),
    path("locations/", views.square_login, name="locations"),
    path("create_subscription/", views.create_subscription, name="create_subscription"),
    path("all_subscriptions/", views.SubscriptionsListView.as_view(), name="all_subscriptions"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("authorize/", views.authorize, name="authorize"),
    path("obtain_merchant_token/", views.obtain_merchant_token, name="obtain_merchant_token"),
    path("club/<slug:slug>/", DetailView.as_view(model=models.Club), name="club_detail"),
    path("clubs/", ListView.as_view(model=models.Club), name="clubs"),
    
]

urlpatterns += [path("accounts/", include("django.contrib.auth.urls")),]