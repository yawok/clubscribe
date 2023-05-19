from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Venue(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=48)
    description = models.TextField()
    polygon = models.PolygonField()
    
    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=48)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    merchant_access_token = models.CharField()

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=48)
    description = models.TextField(null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Membership(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField()
    subscription_id = models.CharField()

    def __str__(self):
        return f"{self.subscriber} - {self.club}"


class SubscriptionPlan(models.Model):
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=100)
    name = models.CharField(max_length=256)
    
    def __str__(self):
        return self.name