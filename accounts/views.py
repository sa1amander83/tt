from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View

from accounts.forms import SignUpForm, SignInForm


# Create your views here.
class SignUpView(View):
    """ User registration view """

    template_name = "accounts/signup.html"
    form_class = SignUpForm

    def get(self, request, *args, **kwargs):
        forms = self.form_class()
        context = {"form": forms}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect("accounts:signin")
        context = {"form": forms}
        return render(request, self.template_name, context)




class SignInView(View):
    """ User registration view """

    template_name = "accounts/signin.html"
    form_class = SignInForm

    def get(self, request, *args, **kwargs):
        forms = self.form_class()
        context = {"form": forms}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            phone_number = forms.cleaned_data["phone_number"]
            password = forms.cleaned_data["password"]
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                login(request, user)
                return redirect("tt:home")
        context = {"form": forms}
        return render(request, self.template_name, context)


def logout_view(request):
    logout(request)
    request.session.flush()

    return redirect("accounts:logout")


def restore_view(request):
    return render(request, "accounts/restore.html")
