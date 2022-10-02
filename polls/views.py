from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    """Home page"""
    return HttpResponse("Hello, world! Welcome to my polling app. Ready to vote?")

