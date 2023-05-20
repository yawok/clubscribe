from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("create_club/", views.CreateClubView.as_view(), name="create_club"),
    path("locations/", views.square_login, name="locations"),
    path("create_subscription/", views.create_subscription, name="create_subscription"),
    path("all_subscriptions/", views.SubscriptionsListView.as_view(), name="all_subscriptions"),
    path("signup/", views.SignupView.as_view(), name="signup"),
]

urlpatterns += [path("accounts/", include("django.contrib.auth.urls")),]