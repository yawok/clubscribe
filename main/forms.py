from django import forms
from django.contrib.auth import models 
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from . import models
import logging

logger = logging.getLogger(__name__)

class ClubForm(forms.ModelForm):
    class Meta:
        model = models.Club
        fields = ("name", "description", )
        
        
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("first_name", "last_name", "email",)
        field_classes = {"email": UsernameField}
        

    def send_mail(self):
        logger.info(f"Sending signup email for email={self.cleaned_data['email']}")
        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            "Welcome to Clubscribe",
            message,
            "site@clubscribe.com",
            [self.cleaned_data["email"]],
            fail_silently=True,
        )
        
class CreateSubscriptionForm(forms.Form):
    PERIODS = (
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("YEARLY", "Yearly")
    )
    name = forms.CharField(max_length=128)
    period = forms.ChoiceField(choices=PERIODS)
    amount = forms.CharField(max_length=4)
    

