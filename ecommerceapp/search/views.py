from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import render
from shop.models import Product

def searchview(request):
    p=None
    query=""
    if(request.method=="POST"):
        query=request.POST['s']
        if query:
            p=Product.objects.filter(Q(name__icontains=query)   |  Q(price__icontains=query))

    return render(request,'search.html',{'Product':p,'query':query})
