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
        

class AuthenticationForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ("email", "password")
        hidden_fields = ("password")
    
    def __init__(self, *args, **kwargs):
        # first call the 'real' __init__()
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # then do extra stuff:
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder': 'Password'})
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class CreateSubscriptionForm(forms.Form):
    PERIODS = (
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("ANNUAL", "Annual")
    )
    
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256)
    period = forms.ChoiceField(choices=PERIODS)
    price = forms.CharField(max_length=6)
    club = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Club.objects.filter(owner=user)
        self.fields["club"].queryset = queryset
    


