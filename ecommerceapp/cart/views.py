from django.shortcuts import render,redirect
from cart.models import cart
from django.views.decorators.csrf import csrf_exempt
from shop.models import product
import razorpay

def addtocart(request,i):
    p=product.objects.get(id=i)
    u=request.user

    try:
        c=cart.objects.get(user=u,product=p)
        print(c)
        c.quantity+=1
        p.stock-=1
        p.save()
        c.save()

    except:
        c=cart.objects.create(product=p,user=u,quantity=1)
        p.stock-= 1
        p.save()
        c.save()

    return redirect('cart:cartview')


def cartview(request):
    u=request.user
    c=cart.objects.filter(user=u)
    # to calculate Total view
    total=0
    for i in c:
        total+=i.quantity*i.product.price
    context={'cart':c,'total':total}
    return render(request,'addtocart.html',context)

def cartremove(request,i):
    u=request.user
    p=product.objects.get(id=i)
    c=cart.objects.get(user=u,product=p)
    if (c.quantity >1):
        c.quantity-=1
        c.save()
        p.stock += 1
        p.save()

    else:
        c.delete()
        p.stock+=1
        p.save()
    return redirect('cart:cartview')

    # try:
    #     c=cart.objects.get(user=u,product=p)
    #     c.quantity -= 1
    #     p.stock += 1
    #     p.save()
    #     c.save()
    #
    # except:
    #     c = cart.objects.create(product=p, user=u, quantity=1)
    #     p.stock += 1
    #     p.save()
    #     c.save()

from cart.models import payment,orderdetails
def delete(request,i):
    u = request.user
    p = product.objects.get(id=i)

    try:

        c = cart.objects.get(user=u, product=p)
        c.delete()
        p.stock += c.quantity
        p.save()

    except:
        pass

    return redirect('cart:cartview')



def orderform(request):
    if request.method=="POST":
        # read the form fields
        a=request.POST['a']
        n=request.POST['n']
        pn=request.POST['p']

# for calculating total bill amount
        u=request.user
        c=cart.objects.filter(user=u)

        total=0
        for i in c:
            total+=i.product.price*i.quantity
        print(total)


        #Razorpay client connection
        client=razorpay.Client(auth=('rzp_test_6bZCEZNX77X880','hZu40aloZzTidethlk5aNnPR'))

        #Razorpay order creation
        response_payment=client.order.create(dict(amount=total*100,currency='INR'))
        order_id=response_payment['id']  #retrieve the order id from response
        status=response_payment['status']  #retrieve the status from response
        if (status=="created"):
            p=payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()

            for i in c:
                o=orderdetails.objects.create(product=i.product,user=i.user,phone=pn,address=a,pin=n,order_id=order_id)
                o.save()
            context={'payment':response_payment,'name':u.username}  # sends the response from views to payment.html
            return render(request, 'payment.html',context)


    return render(request,'orderform.html')


from django.contrib.auth.models import User
from django.contrib.auth import login
@csrf_exempt
def payment_status(request,p):
    user=User.objects.get(username=p)  #retrieve user object
    login(request,user)

    response=request.POST  #razorpay response after successful payment
    print(response)

    #To check the validity(authenticity) of razorpay payment details received by application

    param_dict={
        'razorpay_order_id':response['razorpay_order_id'],
        'razorpay_payment_id':response['razorpay_payment_id'],
        'razorpay_signature':response['razorpay_signature']
    }

    client = razorpay.Client(auth=('rzp_test_6bZCEZNX77X880','hZu40aloZzTidethlk5aNnPR'))
    try:
        status=client.utility.verify_payment_signature(param_dict)

        print(status)

        p=payment.objects.get(order_id=response['razorpay_order_id']) # After successful payment retrieve the payment record matching with response['order_id']
        print(p)
        p.razorpay_payment_id=response['razorpay_payment_id'] #assigns response payment id to razorpay_payment_id
        p.paid=True
        p.save()


        o=orderdetails.objects.filter(order_id=response['razorpay_order_id'])  # After successful payment retrieve the order_details records matching with response
        print(o)
        for i in o:
            i.payment_status="completed" #assigns "completed" to payment_status in each record
            i.save()

        # To remove cart items for a particular user after successful payment
        c=cart.objects.filter(user=user)
        c.delete()

    except:
        pass

    return render(request,'payment-status.html')




def your_order(request):
    u=request.user
    o=orderdetails.objects.filter(user=u,payment_status='completed')
    context={'order':o}
    return render(request,'your_order.html',context)