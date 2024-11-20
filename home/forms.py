from django import forms

from .models import WaitingListSignup


class WaitingListSignupForm(forms.ModelForm):
    class Meta:
        model = WaitingListSignup
        fields = ["email", "referred_by"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "jamie@example.com"}),
            "referred_by": forms.HiddenInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if WaitingListSignup.objects.filter(email=email).exists():
            raise forms.ValidationError("You are already on the waiting list.")
        return email
