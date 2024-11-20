import nh3
from django.http import HttpRequest
from django.shortcuts import render

from .forms import WaitingListSignupForm
from .models import WaitingListSignup

REFERRAL_QUERY_PARAM = "ref"


def join_waiting_list(request: HttpRequest):
    initial_data = request.POST.copy()
    if "ref" in request.GET:
        initial_data["referred_by_code"] = request.GET[REFERRAL_QUERY_PARAM]

    form = WaitingListSignupForm(initial_data)

    if request.method == "POST":
        form.full_clean()

        if form.is_valid():
            sanitized_email = nh3.clean(form.cleaned_data["email"])
            referral_code = nh3.clean(form.cleaned_data.get("referred_by_code", ""))

            try:
                referred_by = WaitingListSignup.objects.get(referral_code=referral_code)
            except WaitingListSignup.DoesNotExist:
                referred_by = None

            obj = WaitingListSignup(
                email=sanitized_email,
                referred_by=referred_by,
            )
            obj.save()

            return render(
                request,
                "home/waiting_list_signup_success.html",
                {
                    "referral_code": obj.referral_code,
                },
            )

    return render(
        request,
        "home/waiting_list_signup_form.html",
        {
            "form": form,
        },
    )
