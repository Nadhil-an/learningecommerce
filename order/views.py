from django.shortcuts import render,redirect
from cart.models import CartItem
from django.http import JsonResponse,HttpResponse
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from store.models import Product
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

##template invoice pdf
from django.template.loader import get_template
from xhtml2pdf import pisa
import io


# Create your views here.
def placeorder(request,total=0,quantity=0):

  current_user = request.user

  cart_items = CartItem.objects.filter(user=current_user)
  cart_count = cart_items.count()
  if cart_count <=0 :
    return redirect('store')
  
  grand_total = 0
  tax = 0
  for cart_item in cart_items:
    total += (cart_item.product.price * cart_item.quantity)
    quantity += cart_item.quantity
  tax = (2 * total)/100
  grand_total = total+tax

  
  

  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      data = Order()
      data.user = current_user
      data.first_name = form.cleaned_data['first_name']
      data.last_name = form.cleaned_data['last_name']
      data.phone = form.cleaned_data['phone']
      data.email = form.cleaned_data['email']
      data.address_line_1 = form.cleaned_data['address_line_1']
      data.address_line_2 = form.cleaned_data['address_line_2']
      data.country = form.cleaned_data['country']
      data.state = form.cleaned_data['state']
      data.city = form.cleaned_data['city']
      data.order_note = form.cleaned_data['order_note']
      data.order_total = grand_total
      data.tax = tax
      data.ip = request.META.get('REMOTE_ADDR')
      data.save()

        # generate order number
      yr = int(datetime.date.today().strftime('%Y'))
      dt = int(datetime.date.today().strftime('%d'))
      mt = int(datetime.date.today().strftime('%m'))
      d = datetime.date(yr, mt, dt)
      current_date = d.strftime("%Y%m%d")
      order_number = current_date + str(data.id)
      data.order_number = order_number
      data.save()


      context = {
          'order': data,
          'cart_items': cart_items,
          'total': total,
          'tax': tax,
          'grand_total': grand_total,
      }
      return render(request, 'payment.html', context)

    else:
      return redirect('checkout')

def payments(request):
  body = json.loads(request.body.decode('utf-8'))
 
  order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

  payment = Payment(
    user = request.user,
    payment_id = body['transID'],
    payment_method = body['payment_method'],
    amount_paid = body['amount'],
    status = body['status']
  )
  payment.save()
  order = Order.objects.get(user=request.user, is_ordered=False)
  order.payment = payment
  order.is_ordered = True
  order.save()

#move cart items into Order Product
  cart_items = CartItem.objects.filter(user=request.user)

  for item in cart_items:
      orderproduct = OrderProduct()
      orderproduct.order_id = order.id
      orderproduct.payment = payment
      orderproduct.user_id = request.user.id
      orderproduct.product_id = item.product_id
      orderproduct.quantity = item.quantity
      orderproduct.product_price = item.product.price
      orderproduct.ordered = True
      orderproduct.save()


  #reduce the quantity of sold product
      product = Product.objects.get(id=item.product_id)
      product.stock -= 1
      product.save()

  #clear the cartItem
  CartItem.objects.filter(user=request.user).delete()

  #send the order receive email
  mail_subject = 'Your order has been recieved'
  message      = render_to_string('order_recieve.html',{
                'user'   :request.user,
                'order'   : order,
            })

  to_email    = request.user.email
  send_email  = EmailMessage(mail_subject, message, to=[to_email])
  send_email.send()


  #send order number and transaction id back to senddata method via jsonResponse
  data = {
    'order_number':order.order_number,
    'transID':payment.payment_id,
  }

  return JsonResponse(data)




def ordercomplete(request):

  order_number = request.GET.get('order_number')
  transID = request.GET.get('payment_id')

  try:
    order = Order.objects.get(order_number=order_number,is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)

    payment = Payment.objects.get(payment_id=transID)

    subtotal = 0
    for i in ordered_products:
      subtotal += i.product_price * i.quantity

    context = {
      'order' : order,
      'ordered_products' :ordered_products,
      'order_number':order.order_number,
      'transID':payment.payment_id,
      'payment':payment,
      'subtotal':subtotal
    }
    return render(request,'order_complete.html',context)
  except (Payment.DoesNotExist,Order.DoesNotExist):
    return redirect('home')
  

def download_invoice_pdf(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=order.payment.payment_id)

        subtotal = 0
        for item in ordered_products:
            subtotal += item.product_price * item.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal
        }

        template_path = 'invoice_pdf.html'
        template = get_template(template_path)
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order_number}.pdf"'

        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors with PDF generation <pre>' + html + '</pre>')
        return response

    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')


