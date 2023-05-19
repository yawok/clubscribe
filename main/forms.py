from django import forms
from . import models


class ClubForm(forms.ModelForm):
    class Meta:
        model = models.Club
        fields = ("name", "description", )

        
class CreateSubscriptionForm(forms.Form):
    PERIODS = (
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
    )
    CURRENCY = (
        ("USD", "US Dollar"),
        # ("GHS", "Ghana Cedi"),
    )
    name = forms.CharField(max_length=128)
    period = forms.ChoiceField(choices=PERIODS)
    amount = forms.CharField(max_length=4)
    currency = forms.ChoiceField(choices=CURRENCY)