from django.shortcuts import render 
from django.http import HttpResponse


def index(request):
    context = {'users': ['a', 'b', 'c']}
    return render(request, 'my_app/index.html', context)

def hello(request, name: str):
    context = {'username': name.capitalize()}
    return render(request, 'my_app/index.html', context)