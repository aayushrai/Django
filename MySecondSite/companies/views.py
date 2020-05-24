from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from  rest_framework import status
from .models import Stock
from .serializer import StockSerializer

# lists of all stocks or create a new one
# stocks/
class StockList(APIView):

    def get(self,request):
        stocks = Stock.objects.all()
        serialzer = StockSerializer(stocks,many=True)
        return Response(serialzer.data)

    def post(self):
        pass