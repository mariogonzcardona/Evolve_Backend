from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def home(request):
    return render(request, "core/home.html")

def health(_): # mejor para el pipeline
    return JsonResponse({"status": "ok"})