from django.shortcuts import render

from details.models import movie


def home(request):

        k=movie.objects.all()
        context={'movie':k}
        return render(request,'home.html',context)

def add(request):
    if(request.method=="POST"):
        t=request.POST['t']
        d=request.POST['d']
        l=request.POST['l']
        y=request.POST['y']
        i=request.FILES['i']
        b=movie.objects.create(title=t,description=d,language=l,year=y,poster=i)
        b.save()

    return render(request,'add.html')

def booking(request):
    return render(request,'booking.html')

def details(request,p):
    m=movie.objects.get(id=p)
    context={'movie':m}
    return render(request,'details.html',context)
