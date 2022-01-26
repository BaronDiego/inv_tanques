from django.shortcuts import render
import requests

# Create your views here.

def api_json(request):
    response = requests.get('https://invtanquesappgranel.pythonanywhere.com/api/dataBun/')
    todos = response.json()
    return render(request, 'consumirapi/data.html', {'todos': todos})
