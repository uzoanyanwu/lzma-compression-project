from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

def index(request):
    return render(request, "users/index.html")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()   
    return render(request, "users/signup.html")

