from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
#from .models import Employee


def index(request):
    #e = Employee(unitId=1)
    #data = serializers.serialize("python", e.objects)
    #context = {
    #    'data': data
    #}
    return render(request, 'index.html')#, context)
    #return HttpResponse("aaa")

