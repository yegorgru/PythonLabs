from django.http import HttpResponse
from django.shortcuts import render
from .models import Employee
from .forms import UserForm


def index(request):
    form = UserForm(request.POST or None, initial={'unit_id': 0})
    id = 0
    if form.is_valid():
        id = form.cleaned_data.get("unit_id")
    data = list(Employee.objects.all().filter(unitId=int(id)))
    print(data)
    context = {
        'data': data,
        'form': form
    }
    return render(request, 'index.html', context)
    #return HttpResponse("aaa")

