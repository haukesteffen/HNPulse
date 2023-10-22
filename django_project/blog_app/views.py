from django.shortcuts import render
from django.http import HttpResponse
from .hnfuncs import hnquery

def display(request, id):
    text = hnquery(id)
    return render(request, 'template.html', {'text': text})