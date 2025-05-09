from django.shortcuts import render
from django.views.generic import View


# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "main/index.html")

def page404(request, exception):
    return render(request, "main/404.html")

def terms(request):
    return render(request, "main/terms.html")

def about_view(request):
    return render(request, "main/about.html")

def contacts_view(request):
    user = request.user  # текущий пользователь

    context = {
        'user': user,
        # Можно добавить другие данные, если нужно
    }

    return render(request, "main/contacts.html", context)