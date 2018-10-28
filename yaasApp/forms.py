from django import forms
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import ugettext as _

from yaasApp.models import *


#Creating forms

class CreateAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ('title', 'description', 'end_date', 'minimum_price')

    def clean(self):
        cleaned_data = super(CreateAuctionForm, self).clean()

        if "end_date" in cleaned_data and not (timezone.now() + timedelta(days=3)) <= cleaned_data.get("end_date"):
            msg = u"End date is at least 72 hours from now"
            self._errors["end_date"] = self.error_class([msg])

        return cleaned_data


class EditAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ('description',)


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_("First name"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Last name"))
    email = forms.EmailField(required=True, label=_("Email"))

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EditUserForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
    email = forms.EmailField(label=_("Email"))


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('bid',)

    updated = forms.DateTimeField(widget=forms.HiddenInput, required=False)


class ConfirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
