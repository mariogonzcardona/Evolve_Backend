from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "core/home.html")

def health(_): # mejor para el pipeline
    return JsonResponse({"status": "ok"})