from django import forms


class WaitingListSignupForm(forms.Form):
    referred_by_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "jamie@example.com",
            }
        ),
    )
