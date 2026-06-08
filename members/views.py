from django.shortcuts import render

def team_view(request):
    return render(request, 'members/team.html')

def login_view(request):
    return render(request, 'members/login.html')

def register_view(request):
    return render(request, 'members/register.html')