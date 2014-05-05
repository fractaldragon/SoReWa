import datetime
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from SoReWaApp.models import Category, Product, Table, Order
# Create your views here.


def create_menu(request):
    try:
        category = Category.objects.all()
    except Category.DoesNotExist:
        print "No Categories in the database yet."
        food_category = Category(name='Food', description='Fine selection of food')
        drinks_category = Category(name='Drinks', description='Fine selection of drinks')
        food_category.save()
        drinks_category.save()
    else:
        #show categories and products
        pass


def choose_table(request):
    """# Set a session value:
request.session["fav_color"] = "blue"

# Get a session value -- this could be called in a different view,
# or many requests later (or both):
fav_color = request.session["fav_color"]

# Clear an item from the session:
del request.session["fav_color"]

# Check if the session has a given key:
if "fav_color" in request.session:
    ..."""

    try:
        table_list = Table.objects.all()
        print table_list

    except Table.DoesNotExist:
        print "No tables in db."

    error = False
    if "table_number" in request.session:
        print "session table number: %s" % request.session["table_number"]

        try:
            session_table = Table.objects.get(number=request.session["table_number"])
            if session_table.is_occupied:
                print "got table %s and table is occupied" % request.session["table_number"]
                return redirect('SoReWaApp.views.table')
            else:
                print "got session but table is NOT occupied"
                del request.session["table_number"]
                return render(request, 'table_selector.html', {'error': error, 'table_list': table_list})

        except Table.DoesNotExist:
            print "Table does not exist in the system"

    else:
        print"no table_number in session"
        if 'table_number' in request.GET:
            table_number = request.GET['table_number']

            if not table_number or not (table_number.isdigit()):
                print "error"
                error = True
            else:
                #if number is occupied
                try:
                    chosen_table = Table.objects.get(number=table_number)

                    if chosen_table.is_occupied:
                        print "table is occupied"
                        error = True
                    else:
                        request.session["table_number"] = "%s" % table_number
                        chosen_table.is_occupied = True
                        chosen_table.save()
                        #table_order = Order(table_number=table_number, date=datetime.datetime.now())
                        #table_order.save()
                        print "table number %s assigned" % table_number
                        return redirect('SoReWaApp.views.table')

                except Table.DoesNotExist:
                    print "table does not exist"
                    error = True

    return render(request, 'table_selector.html', {'error': error, 'table_list': table_list})


def table(request):
    #todo if table occuppied, i have number, and order show order in table
    #todo use var for waiter call, order, and bill to pop alerts or to block buttons
    if "table_number" in request.session:
        try:
            table_occupied = Table.objects.get(number=request.session["table_number"])
            if not table_occupied.is_occupied:
                table_occupied.is_occupied = True
                table_occupied.save()
                return render(request, 'table.html')
                #return redirect('SoReWaApp.views.choose_table') # todo check the logic with table not ocupied but have session
            #category = Category.objects.all()
            category = Category.objects.filter(is_available=True)

        except Category.DoesNotExist:
            print "No Categories in the database yet."
            return render(request, 'table.html')

        else:
            # todo show hide buttons on calls
            #show categories and products
            return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})

    else:
        return redirect('SoReWaApp.views.choose_table')


def get_products_from_category(request, offset):
    try:
        offset = str(offset)
        print offset
        if len(offset) <= 50 and len(offset) != 0:
            category = Category.objects.get(name=offset, is_available=True)
            return render(request, 'products.html', {'products_list': category.products.all()})
        else:
            all_products = Product.objects.all()
            return render(request, 'products.html', {'products_list': all_products})

    except Category.DoesNotExist:
        print "No Categories in the database yet."
        raise Http404()


def add_to_order(request):
    if "table_number" in request.session:
        print "session table number: %s" % request.session["table_number"]

        try:
            session_table = Table.objects.get(number=request.session["table_number"])
            if session_table.is_occupied:
                print "got table %s and table is occupied" % request.session["table_number"]
                if request.method == 'POST':
                    print "tengo post"
                    if request.POST.get('product_name', ''):
                        product_name = request.POST['product_name']

                        if len(product_name) <= 100:  #todo use a var instead of a number
                            try:
                                chosen_product = Product.objects.get(name=product_name)

                                if "table_order_number" in request.session:
                                    t = Table.objects.get(number=request.session["table_number"])
                                    order = Order(order_number=request.session["table_order_number"],
                                                  table_number=t,
                                                  date=datetime.datetime.now(), sent_to_kitchen=False,
                                                  product=chosen_product)
                                    order.save()
                                    #return redirect('SoReWaApp.views.view_table_order')

                                    try:
                                        tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                                          order_number=request.session["table_order_number"])
                                        return render(request, 'view_order.html', {'products_list': tableorder, 'show_notification': True, 'product_name': product_name, 'message': " has been added to order"})

                                    except Order.DoesNotExist:
                                        print "No Order in the database yet."
                                        raise Http404()

                                else:

                                    try:
                                        next_order_number = Order.objects.filter(
                                            table_number=request.session["table_number"])
                                        val = 0
                                        for i in next_order_number:
                                            if i.order_number > val:
                                                val = i.order_number
                                        val += 1
                                        t = Table.objects.get(number=request.session["table_number"])
                                        order = Order(order_number=val,
                                                      table_number=t,
                                                      date=datetime.datetime.now(), sent_to_kitchen=False,
                                                      product=chosen_product)
                                        order.save()
                                        request.session["table_order_number"] = "%s" % val
                                        return redirect('SoReWaApp.views.view_table_order')

                                    except Table.DoesNotExist:
                                        print "Table does not in order table"
                                        t = Table.objects.get(number=request.session["table_number"])
                                        order = Order(order_number=1,
                                                      table_number=t,
                                                      date=datetime.datetime.now(), sent_to_kitchen=False,
                                                      product=chosen_product)
                                        order.save()
                                        request.session["table_order_number"] = "1"
                                        return redirect('SoReWaApp.views.view_table_order')

                                    pass

                                """
                                sino hay orden de mesa la creo con la mesa y un nuevo numero de orden, este numero lo guardo en la session de la mesa,
                                  pregunto si el numero ya existe en la bd sino existe, creo la nueva orden
                                   si ya existe y no esta pagada en table orders agrego producto
                                   si ya esta pagada elijo otro numero y creo una nueva orden
                                """
                                #session_table.order.products_list.add(chosen_product)

                            except Product.DoesNotExist:
                                print "product does not exist"
                                return redirect('SoReWaApp.views.view_table_order')

                        else:
                            print "Product name too long!"
                            return redirect('SoReWaApp.views.view_table_order')

                    else:
                        print "No product Name"
                        return redirect('SoReWaApp.views.view_table_order')
                else:
                    print"no tengo post"
                    return redirect('SoReWaApp.views.view_table_order')

            else:
                print "got session but table is NOT occupied"
                del request.session["table_order_number"]
                del request.session["table_number"]
                return redirect('SoReWaApp.views.choose_table')

        except Table.DoesNotExist:
            print "Table does not exist in the system"
            return redirect('SoReWaApp.views.choose_table')
    else:
        return redirect('SoReWaApp.views.choose_table')


def remove_from_order(request):  #todo check if order number exist for the given table, also in add product
    if "table_number" in request.session:
        if "table_order_number" in request.session:
            try:

                session_table = Table.objects.get(number=request.session["table_number"])

                if session_table.is_occupied:
                    if request.method == 'POST':
                        print "Remove from table:got post"
                        if request.POST.get('product_name', ''):
                            product_name = request.POST['product_name']

                            if len(product_name) <= 100:  #todo use a var instead of a number
                                try:
                                    chosen_product = Product.objects.get(name=product_name)
                                    product_list = Order.objects.filter(table_number=request.session["table_number"],
                                                                        order_number=request.session["table_order_number"],
                                                                        product=chosen_product)
                                    if product_list: # if i have multiple, i have to check just 1 to remove if it hasnt been sent to kitchen

                                        for p in product_list:
                                            if not p.sent_to_kitchen:
                                                p.delete()
                                                try:
                                                    tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                                          order_number=request.session["table_order_number"])
                                                    return render(request, 'view_order.html', {'products_list': tableorder, 'show_notification': True, 'product_name': product_name, 'message': " has been Removed from order"})

                                                except Order.DoesNotExist:
                                                    print "No Order in the database yet."
                                                    raise Http404()
                                                else:
                                                    print "EMPTY ORDER!!!"

                                    #return redirect('SoReWaApp.views.view_table_order')
                                    try:
                                        tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                              order_number=request.session["table_order_number"])
                                        return render(request, 'view_order.html', {'products_list': tableorder, 'show_notification': True, 'message': " already ordered, cannot remove product, call a waiter if you need something"})

                                    except Order.DoesNotExist:
                                        print "No Order in the database yet."
                                        raise Http404()
                                    else:
                                        print "EMPTY ORDER!!!"



                                except Product.DoesNotExist:
                                    print "Remove from table: product not in order"
                                    return redirect('SoReWaApp.views.view_table_order')
                            else:
                                print "Remove from table:product name too long"
                                return redirect('SoReWaApp.views.view_table_order')
                        else:
                            print "Remove from table: No product Name"
                            return redirect('SoReWaApp.views.view_table_order')
                    else:
                        print "Remove from table: no post"
                        return redirect('SoReWaApp.views.view_table_order')
                else:
                    print "Remove from order: Table not occupied"
            except Table.DoesNotExist:
                print "Remove from order:Table does not exist"
                return redirect('SoReWaApp.views.choose_table')

        else:
            print "Remove from order: No order in session"
            return redirect('SoReWaApp.views.table')

    else:
        print "Remove from order: No table number in session"
        return redirect('SoReWaApp.views.choose_table')


    """
         p = Publisher.objects.get(name="O'Reilly")
        p.delete()
        Publisher.objects.filter(country='USA').delete()
        Publisher.objects.all().delete()
         Publisher.objects.filter(country='USA').delete()
    """


def view_table_order(request):

    if "table_number" in request.session:
        if "table_order_number" in request.session:  #el primero sino lo tengo me lleva  a elegir numero mesa, el segundo sino lo tengo me lleva a la mesa
            print "found table number: %s and order: %s" % (
                request.session["table_number"], request.session["table_order_number"])

            try:
                tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                  order_number=request.session["table_order_number"])

                if tableorder:
                    return render(request, 'view_order.html', {'products_list': tableorder})
                else:
                    return render(request, 'view_order.html', {'show_notification': True, 'message': "You dont have products in the order yet."})

            except Order.DoesNotExist:
                print "No Order in the database yet."
                return render(request, 'view_order.html', {'show_notification': True, 'message': "You dont have an order yet."})
        else:
            print "No Order in session "
            return render(request, 'view_order.html', {'show_notification': True, 'message': "You dont have an order yet."})

        return render(request, 'view_order.html')

    else:
        return redirect('SoReWaApp.views.choose_table')


def call_waiter(request):
    if "table_number" in request.session:
        print('Call Waiter from table: %s') % request.session["table_number"]
        try:
            table_waiter = Table.objects.get(number=request.session["table_number"])
            table_waiter.calls_waiter = True
            table_waiter.save()
        except Table.DoesNotExist:
            return redirect('SoReWaApp.views.choose_table')
        else:
            try:
                category = Category.objects.filter(is_available=True)
            except Category.DoesNotExist:
                print "No Categories in the database yet."
                return render(request, 'table.html')
            else:
                #show categories and products
                return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})
    else:
        return redirect('SoReWaApp.views.choose_table')


def call_order(request):
    print "entre!"
    if "table_number" in request.session:
        if "table_order_number" in request.session:
            try:
                product_list = Order.objects.filter(table_number=request.session["table_number"],
                                                    order_number=request.session["table_order_number"]
                                                    )
                if product_list:
                    has_pending_products = False
                    for p in product_list:
                        if not p.sent_to_kitchen:
                            has_pending_products = True
                            p.sent_to_kitchen = True
                            p.save()

                    if has_pending_products:
                        try:
                            order_table = Table.objects.get(number=request.session["table_number"])
                            order_table.calls_order = True
                            order_table.save()

                        except Table.DoesNotExist:
                            print "Call Order: table does not exist"
                        else:
                            try:
                                category = Category.objects.filter(is_available=True)
                            except Category.DoesNotExist:
                                print "No Categories in the database yet."
                                return render(request, 'table.html')
                            else:
                                #show categories and products
                                return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})

                    else: # todo show alert, notification , a order once made cannot be modified by client, if you have you'll need to call a waiter
                        print"Call Order: no pending products"
                        try:
                                category = Category.objects.filter(is_available=True)
                        except Category.DoesNotExist:
                            print "No Categories in the database yet."
                            return render(request, 'table.html')
                        else:
                            #show categories and products
                            return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})

                else:
                    print("Call Order: product list empty")
                    return redirect('SoReWaApp.views.table')

            except Order.DoesNotExist:
                print "Call Order: order doesnt exist"

        else:
            print('Call Order: has no table order number in session')  # no product has been added to order once
            return redirect('SoReWaApp.views.table')
    else:
        return redirect('SoReWaApp.views.choose_table')


def call_bill(request):
    # if i have no products cant call bill
    # if i have products, but they haven't been sent to the kitchen cant call bill
    # products that have not been sent to the kitchen will be removed, and the total wil be calculated with the ones that have been sent to the kitchen
    if "table_number" in request.session:
        if "table_order_number" in request.session:
            # try catch missing here
            table_calling_bill = Table.objects.get(number=request.session["table_number"])
            table_order_products = Order.objects.filter(table_number=request.session["table_number"], order_number=request.session["table_order_number"])
            has_product_to_pay = False
            for order_product in table_order_products:
                if order_product.sent_to_kitchen:
                    has_product_to_pay = True
                    if not table_calling_bill.calls_bill:
                        table_calling_bill.calls_bill = True
                        table_calling_bill.save()
                        print "table %s wants to pay" % request.session["table_number"]

                        for p in table_order_products:
                            if not p.sent_to_kitchen:
                                print "%s removed" % p.product.name
                                p.delete()
                    else:
                        for p in table_order_products:
                            if not p.sent_to_kitchen:
                                print "%s removed" % p.product.name
                                p.delete()

                    break
            if has_product_to_pay:
                print "has to pay"
                #todo  notify user and block buttons, delete order var and show table order and total,this page must redirect to table, again for next users

                try:
                    tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                      order_number=request.session["table_order_number"],sent_to_kitchen=True)
                    order_total = 0

                    for p in tableorder:
                        if p.sent_to_kitchen:
                            order_total = order_total+p.product.price
                    ###################################
                    print 'el costo total es %s' % order_total
                    return render(request, 'view_order.html', {'products_list': tableorder, 'show_notification': True, 'message': "Your Order cost is: $ %s " % order_total })

                except Order.DoesNotExist:
                    print "No Order in the database yet."
                    raise Http404()
                return redirect('SoReWaApp.views.table')
            else:
                print "doesnt pay "
                return redirect('SoReWaApp.views.table',)
        else:
            print "Call Bill: no table order number"
            return redirect('SoReWaApp.views.table')
    else:
        print "Call Bill: No table number!!!"
        return redirect('SoReWaApp.views.choose_table')











"""Well, that is weird. MayRelatedManager definitely *does* have an
attribute 'remove'. With these basic models:

class Category(models.Model):
    title = models.CharField(_('title'), max_length=100)

class Post(models.Model):
    title = models.CharField(_('title'), max_length=200)
    categories = models.ManyToManyField(Category)


the following works fine:
>>> from blog.models import Post, Category
>>> p=Post.objects.create(title='dan')
>>> c=Category.objects.create(title='category')
>>> p.categories.all()
[]
>>> p.categories.add(c)
>>> p.categories.all()
[<Category: category>]
>>> p.categories.remove(c)
>>> p.categories.all()
[]

So it works for me, I can't imagine what is happening with your setup.
What version of Django are you using? """




