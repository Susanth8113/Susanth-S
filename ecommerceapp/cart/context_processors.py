from cart.models import cart

def count_items(request):
    count=0
    if request.user.is_authenticated:
        u=request.user
        c=cart.objects.filter(user=u)
        for i in c:
            count+=i.quantity
    return{'count':count}