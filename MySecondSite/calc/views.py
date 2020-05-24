from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request,'home.html',{'name':"aayush"})

def add(request):
    sum = int(request.POST['num1']) + int(request.POST['num2'])
    return render(request, 'result.html', {'sum':sum })
