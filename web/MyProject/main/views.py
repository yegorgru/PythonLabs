from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from .models import Employee


def index(request):
    data = list(Employee.objects.all().filter(unitId=0))
    print(data)
    context = {
        'data': data
    }
    return render(request, 'index.html', context)
    #return HttpResponse("aaa")

