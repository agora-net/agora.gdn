import nh3
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from .forms import WaitingListSignupForm
from .models import WaitingListSignup


def join_waiting_list(request: HttpRequest):
    if request.method == "POST":
        form = WaitingListSignupForm(request.POST)
        form.full_clean()

        if form.is_valid():
            sanitized_email = nh3.clean(form.cleaned_data["email"])

            obj = WaitingListSignup(email=sanitized_email)
            obj.save()

            return redirect("join_waiting_list_success")

        return render(request, "home/waiting_list_signup.html", {"form": form})

    return HttpResponseNotAllowed(permitted_methods=["POST"])


def join_waiting_list_success(request: HttpRequest):
    return render(request, "home/waiting_list_signup_success.html")
