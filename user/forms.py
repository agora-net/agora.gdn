from django import forms


class StartStripeSubscriptionForm(forms.Form):
    price_id = forms.CharField(
        max_length=128,
        required=True,
    )
