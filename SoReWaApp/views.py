import datetime
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from SoReWaApp.models import Category, Product, Table, Order, TableOrders
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
            category = Category.objects.filter(is_available=True)
            if not table_occupied.is_occupied:
                table_occupied.is_occupied = True
                table_occupied.save()
                return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})
                #return redirect('SoReWaApp.views.choose_table') # todo check the logic with table not ocupied but have session
            #category = Category.objects.all()


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


def get_products(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=/waiter/')
    else:
        try:

            all_products = Product.objects.all().order_by("name")
            return render(request, 'waiter_simple_product_list.html', {'products_list': all_products})

        except Product.DoesNotExist:
            print "No products in the database yet."
            return render(request, 'waiter_simple_product_list.html')


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
                                        table_order = TableOrders.objects.get(table_id=request.session["table_number"], is_paid=False)
                                    except TableOrders.DoesNotExist:
                                            table_order = TableOrders(table_id=t, actual_order=order)
                                            table_order.save()

                                    try:
                                        tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                                          order_number=request.session["table_order_number"])
                                        return render(request, 'view_order.html', {'products_list': tableorder,

                                                                                   'show_notification': True,
                                                                                   'product_name': product_name,
                                                                                   'message': " has been added to order",
                                                                                   'cost': get_table_total(tableorder)})
                                        #return redirect('SoReWaApp.views.view_table_order')

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
                                        table_order = TableOrders(table_id=t, actual_order=order )
                                        table_order.save()
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
                                        table_order = TableOrders(table_id=t, actual_order=order )
                                        table_order.save()
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

                                                #todo check if table order has items if not, check order with order number and if it has them recreates the table order object
                                                try:
                                                    table_order = TableOrders.objects.get(table_id=request.session["table_number"] ,actual_order=request.session["table_order_number"])
                                                except TableOrders.DoesNotExist:
                                                    print "NO TABLE ORDER!!!!"

                                                    try:
                                                        product_list = Order.objects.filter(table_number=request.session["table_number"],
                                                                                       order_number=request.session["table_order_number"])

                                                        t = Table.objects.get(number=request.session["table_number"])
                                                        if product_list:
                                                            table_order = TableOrders(table_id=t, actual_order=product_list[0] )
                                                            table_order.save()
                                                        else:
                                                            return redirect('SoReWaApp.views.view_table_order')

                                                    except Order.DoesNotExist:# no more products in order
                                                        return redirect('SoReWaApp.views.view_table_order')

                                                try:
                                                    tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                                                    order_number=request.session["table_order_number"])
                                                    return render(request, 'view_order.html', {'products_list': tableorder,

                                                                                               'cost': get_table_total(tableorder),
                                                                                               'show_notification': True,
                                                                                               'product_name': product_name,
                                                                                               'message': " has been Removed from order"})
                                                    #return redirect('SoReWaApp.views.view_table_order')
                                                except Order.DoesNotExist:
                                                    print "No Order in the database yet."
                                                    raise Http404()
                                                else:
                                                    print "EMPTY ORDER!!!"

                                    #return redirect('SoReWaApp.views.view_table_order')
                                    try:
                                        tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                              order_number=request.session["table_order_number"])
                                        return render(request, 'view_order.html', {'products_list': tableorder,  'show_notification': True, 'message': " already ordered, cannot remove product, call a waiter if you need something"})

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
                    return render(request, 'view_order.html', {'products_list': tableorder,  'cost': get_table_total(tableorder)})
                else:
                    return render(request, 'view_order.html', {'show_notification': True, 'message': "You dont have products in the order yet.", 'cost': 0})

            except Order.DoesNotExist:
                print "No Order in the database yet."
                return render(request, 'view_order.html', {'show_notification': True, 'message': "You dont have an order yet.", 'cost': 0})
        else:
            print "No Order in session "
            return render(request, 'view_order.html', { 'show_notification': True, 'message': "You dont have an order yet.", 'cost': 0})

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
                if "table_order_number" in request.session:
                    try: # todo check error when calling waiter and table doesnt have order number
                        ordered_product_list = Order.objects.filter(table_number=request.session["table_number"],
                                                        order_number=request.session["table_order_number"],
                                                        sent_to_kitchen=True)
                        if ordered_product_list:
                            return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False, 'show_pay_button': True})
                        else:
                            return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})
                    except Order.DoesNotExist:
                        print "No order."
                        return render(request, 'table.html')
                else:
                    return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False})


    else:
        return redirect('SoReWaApp.views.choose_table')


def call_order(request):
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
                                return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False, 'show_pay_button': True})

                    else: # todo show alert, notification , a order once made cannot be modified by client, if you have you'll need to call a waiter
                        print"Call Order: no pending products"
                        try:
                                category = Category.objects.filter(is_available=True)
                        except Category.DoesNotExist:
                            print "No Categories in the database yet."
                            return render(request, 'table.html')
                        else:
                            #show categories and products
                            return render(request, 'table.html', {'category_list': category, 'load_order': True, 'load_product': False, 'show_pay_button': True})

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


                try:
                    tableorder = Order.objects.filter(table_number=request.session["table_number"],
                                                      order_number=request.session["table_order_number"],sent_to_kitchen=True)
                    order_total = 0

                    for p in tableorder:
                        if p.sent_to_kitchen:
                            order_total = order_total+p.product.price
                    ###################################
                    print 'el costo total es %s' % order_total
                    del request.session["table_order_number"]# todo comment for testing
                    #request.session["table_order_number"] = 0
                    return render(request, 'view_order_total.html', {'products_list': tableorder, 'show_notification': True, 'message': "Your Order cost is: $ %s " % order_total, 'cost': order_total })

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


def waiter_add_product(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/')
    else:
        #need table nr, order nr, product name
        #when adding a product have to do the same with table add product, if he has order id use that id, else assign a new one after cheching
        if "selected_table" in request.session:
            print "waiter add product got selected table %s" % request.session["selected_table"]
            selected_table = request.session["selected_table"]

            product_name = request.POST['product_name']
            chosen_product = Product.objects.get(name=product_name)

            # check if table has actual order
            try:
                table_order = TableOrders.objects.get(table_id=selected_table, is_paid=False)

                next_order_number = Order.objects.filter(table_number=selected_table,sent_to_kitchen=False)

                t = Table.objects.get(number=selected_table)
                order = Order(order_number=table_order.actual_order.order_number,
                              table_number=t,
                              date=datetime.datetime.now(), sent_to_kitchen=False,
                              product=chosen_product)
                order.save()
                try:
                    print "waiter remove product checking more order products!!!!"
                    product_list = Order.objects.filter(table_number=t,
                                                        order_number=table_order.actual_order.order_number)

                    if product_list:
                        return render(request, 'waiter_v_order.html', {'products_list': product_list,
                                                                       'table_number': t.number,
                                                                       'table_order_number': table_order.actual_order.order_number,
                                                                       'show_notification': True,
                                                                       'product_name': product_name,
                                                                       'message': ' Added to Order ',
                                                                       'cost': get_table_total(product_list)})

                    else:
                        return render(request, 'waiter_v_order.html', {'products_list': product_list,
                                                                       'table_number': t.number,
                                                                       'table_order_number': table_order.actual_order.order_number,
                                                                       'show_notification': True,
                                                                       'product_name': product_name,
                                                                       'message': ' Added, No more products in order', 'cost': 0})

                except Order.DoesNotExist:  # no more products in order
                    print "NO MORE PRODUCTS IN CLIENTS ORDER!!!!!!!!!!"
                    return redirect('SoReWaApp.views.waiter_view_table_order ')


            except TableOrders.DoesNotExist:
                print "waiter add product, order does not exist"

                try:
                    next_order_number = Order.objects.filter(
                        table_number=selected_table)
                    val = 0
                    for i in next_order_number:
                        if i.order_number > val:
                            val = i.order_number
                    val += 1
                    t = Table.objects.get(number=selected_table)
                    order = Order(order_number=val,
                                  table_number=t,
                                  date=datetime.datetime.now(), sent_to_kitchen=False,
                                  product=chosen_product)
                    order.save()
                    table_order = TableOrders(table_id=t, actual_order=order )
                    table_order.save()
                    request.session["table_order_number"] = "%s" % val
                    return redirect('SoReWaApp.views.waiter_view_table_order')

                except Table.DoesNotExist:
                    print "Table does not in order table"
                    try:
                        t = Table.objects.get(number=selected_table)
                        order = Order(order_number=1,
                                      table_number=t,
                                      date=datetime.datetime.now(), sent_to_kitchen=False,
                                      product=chosen_product)
                        order.save()
                        table_order = TableOrders(table_id=t, actual_order=order )
                        table_order.save()
                        request.session["table_order_number"] = "1"
                        return redirect('SoReWaApp.views.waiter_view_table_order')
                    except Table.DoesNotExist:
                        print"table to add product doesnt exist"
                        return render(request, 'waiter_v_order.html', {'cost': 0})

        else:
            print "waiter add product didnt get selected table"
            return redirect('SoReWaApp.views.waiter_view_table_order')


def waiter_remove_product(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        # need table nr, order nr, product name
        if request.method == 'POST':
            print "Waiter remove from table:got post"
            if request.POST.get('product_name', ''):
                product_name = request.POST['product_name']
                # todo , on table link check , wen order loads, save table oactual table number and order and use them here
                table_number = request.session['selected_table']
                order_number = request.POST['order_number']

                try:
                    table_number = int(table_number)
                    order_number = int(order_number)

                    if table_number < 100 and table_number != 0 and len(product_name) <= 100:  # url offset has a 2 digit number
                        chosen_product = Product.objects.get(name=product_name)
                        product_list = Order.objects.filter(table_number=table_number,
                                                            order_number=order_number,
                                                            product=chosen_product)

                        if product_list: # if i have multiple, i have to check just 1 to remove

                            for p in product_list:
                                p.delete()

                                try:
                                    table_order = TableOrders.objects.filter(table_id=table_number,
                                                                          actual_order=request.session["table_order_number"])
                                except TableOrders.DoesNotExist:
                                    print "waiter remove product NO TABLE ORDER!!!!"

                                    try:
                                        print "waiter remove product checking more order products!!!!"
                                        product_list = Order.objects.filter(table_number=table_number,
                                                                            order_number=order_number)

                                        t = Table.objects.get(number=table_number)
                                        if product_list:
                                            print "waiter remove product got product list!!!!"
                                            table_order = TableOrders(table_id=t, actual_order=product_list[0] )
                                            table_order.save()
                                            return render(request, 'waiter_v_order.html', {'products_list': product_list,
                                                                                           'table_number': table_number,
                                                                                           'table_order_number': order_number,
                                                                                           'show_notification': True,
                                                                                           'product_name': product_name,
                                                                                           'message': 'Removed from order',
                                                                                           'cost': get_table_total(product_list)})

                                        else:
                                            return render(request, 'waiter_v_order.html', {'products_list': product_list,
                                                                                           'table_number': table_number,
                                                                                           'table_order_number': order_number,
                                                                                           'show_notification': True,
                                                                                           'product_name': product_name,
                                                                                           'message': ' Removed, No more products in order',
                                                                                           'cost': get_table_total(product_list)})

                                    except Order.DoesNotExist:  # no more products in order
                                        print "NO MORE PRODUCTS IN CLIENTS ORDER!!!!!!!!!!"
                                        return redirect('SoReWaApp.views.waiter_view_table_order ')
                                else:
                                    #return redirect('SoReWaApp.views.waiter_view_table_order ')234
                                    break






                        tableorder = Order.objects.filter(table_number=table_number,
                                                          order_number=order_number)
                        return render(request, 'waiter_v_order.html', {'products_list': tableorder, 'table_number': table_number, 'table_order_number': order_number,
                                                                                           'cost': get_table_total(product_list)})
                    else:

                        return redirect('SoReWaApp.views.waiter_view_table_order ')

                except TableOrders.DoesNotExist:
                    print "No table in the database yet."
                    raise Http404()


def waiter_check_tables(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        try:
            #table_list = TableOrders.objects.filter(is_paid=False)
            table_list = Table.objects.filter(is_occupied=True)
    # todo logic if table is occupied
            # if occupied, but no paid , dont give link
            if table_list:
                if 'selected_table' in request.session:
                    return render(request, 'table_list.html', {'table_list': table_list, 'selectedtable': request.session['selected_table']})
                else:
                    return render(request, 'table_list.html', {'table_list': table_list})
            else:
                if 'selected_table' in request.session:
                    del request.session['selected_table']
                return render(request, 'table_list.html')

        except Table.DoesNotExist:
            return render(request, 'table_list.html')
        pass


def waiter_view_table_order(request, offset):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        # need table nr, order nr
        try:
            offset = int(offset)
            try:
                table = Table.objects.get(number=offset)
            except Table.DoesNotExist:
                print "offset number not in table number list"
                raise Http404()
            else:
                print "selected table %s" % offset
                request.session["selected_table"] = offset

            if offset < 100 and offset != 0: # url offset has a 2 digit number
                table_order_list = TableOrders.objects.filter(table_id=offset, is_paid=False)

                if table_order_list:

                    if len(table_order_list) > 1:
                        index = len(table_order_list)-1
                        table_order = table_order_list[index]
                    else:
                        table_order = table_order_list[0]

                    order = Order.objects.filter(table_number=table_order.table_id,
                                                 order_number=table_order.actual_order.order_number)

                    if order:
                        request.session["selected_table_order_number"] = table_order.actual_order.order_number

                    return render(request, 'waiter_v_order.html', {'products_list': order, 'table_number': offset, 'table_order_number':table_order.actual_order.order_number, 'cost': get_table_total(order)})
                else:
                    return render(request, 'waiter_v_order.html', {'cost': 0})

            else:

                return render(request, 'waiter_v_order.html', {'cost': 0})

        except TableOrders.DoesNotExist:
            print "waiter_view_table_order: no table order"

            return render(request, 'waiter_v_order.html', {'cost': 0})


def waiter_view_table_order_added_product(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        # need table nr, order nr
        try:
            if 'selected_table' in request.session:
                selected_table = request.session['selected_table']
            else:
                request.session['selected_table'] = 0
                selected_table = 0
            try:
                table = Table.objects.get(number=selected_table)
            except Table.DoesNotExist:
                print "offset number not in table number list"
                return render(request, 'waiter_v_order.html', )
            else:
                print "selected table %s" % selected_table
                request.session["selected_table"] = selected_table

            if selected_table < 100 and selected_table != 0: # url offset has a 2 digit number
                table_order = TableOrders.objects.get(table_id=selected_table, is_paid=False)

                order = Order.objects.filter(table_number=table_order.table_id,
                                             order_number=table_order.actual_order.order_number)

                if order:
                    request.session["selected_table_order_number"] = table_order.actual_order.order_number

                return render(request, 'waiter_v_order.html', {'products_list': order, 'table_number': selected_table, 'table_order_number':table_order.actual_order.order_number, 'cost': get_table_total(order)})
            else:

                return render(request, 'waiter_v_order.html', {'cost': 0})

        except TableOrders.DoesNotExist:
            print "waiter_view_table_order: no table order"

            return render(request, 'waiter_v_order.html', {'cost': 0})


def waiter_manage_tables(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:

        if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

        else:
            return render(request, 'waiterScreen.html')


def waiter_mark_table_as_paid(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        if 'selected_table' in request.session:
            table_number = request.session['selected_table']

            try:
                table = Table.objects.get(number=table_number)
                table_order = TableOrders.objects.get(table_id=table, is_paid=False)
            except Table.DoesNotExist:
                print "waiter clear table: table number does not exist"
                return redirect('SoReWaApp.views.waiter_manage_tables')
            else:

                table.calls_bill = False
                table_order.is_paid = True
                table.save()
                table_order.save()

                return redirect('SoReWaApp.views.waiter_manage_tables')
        else:
            return redirect('SoReWaApp.views.waiter_manage_tables')


def waiter_clear_table(request):

    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:

        if 'selected_table' in request.session:
            table_number = request.session['selected_table']

            try:
                table = Table.objects.get(number=table_number)

                try:
                    table_order = TableOrders.objects.get(table_id=table, is_paid=False)
                except TableOrders.DoesNotExist:
                    table.is_occupied = False
                    table.calls_bill = False
                    table.calls_order = False
                    table.calls_waiter = False
                    table.save()
                    #return redirect('SoReWaApp.views.waiter_manage_tables')
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'Table is clear %s' % table_number})

            except Table.DoesNotExist:
                print "waiter clear table: table number does not exist"
                pass
            else:
                table.is_occupied = False
                table.calls_bill = False
                table.calls_order = False
                table.calls_waiter = False
                table_order.is_paid = True
                table.save()
                table_order.save()
                #return redirect('SoReWaApp.views.waiter_manage_tables')
                return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'Table is clear %s' % table_number})
        else:
            return redirect('SoReWaApp.views.waiter_manage_tables')


def waiter_attend_waiter_call(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:

        if 'selected_table' in request.session:
            table_number = request.session['selected_table']

            try:
                table = Table.objects.get(number=table_number)
            except Table.DoesNotExist:
                print "waiter clear table: table number does not exist"
                pass
            else:
                if table.calls_waiter:
                    table.calls_waiter = False
                    table.save()
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'attended table %s call' % table_number})
                    #return redirect('SoReWaApp.views.waiter_manage_tables')
                else:
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'table %s has no waiter call' % table_number})
        else:
            return redirect('SoReWaApp.views.waiter_manage_tables')


def waiter_attend_order_call(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:

        if 'selected_table' in request.session:
            table_number = request.session['selected_table']

            try:
                table = Table.objects.get(number=table_number)
            except Table.DoesNotExist:
                print "waiter clear table: table number does not exist"
                pass
            else:
                if table.calls_order:
                    table.calls_order = False
                    table.save()
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'attended table %s Order call' % table_number})
                    #return redirect('SoReWaApp.views.waiter_manage_tables')
                else:
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': ' table %s has no Order call' % table_number})
        else:
            return redirect('SoReWaApp.views.waiter_manage_tables')


def waiter_attend_pay_call(request):
    if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=/waiter/' )
    else:
        if 'selected_table' in request.session:
            table_number = request.session['selected_table']

            try:
                table = Table.objects.get(number=table_number)
                table_order = TableOrders.objects.get(table_id=table, is_paid=False)
            except Table.DoesNotExist:
                print "waiter clear table: table number does not exist"
                pass
            else:
                if table.calls_bill:
                    table.calls_bill = False
                    table_order.is_paid = True
                    table.save()
                    table_order.save()
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'attended table %s Pay Bill call' % table_number})
                    #return redirect('SoReWaApp.views.waiter_manage_tables')
                else:
                    return render(request, 'waiterScreen.html', {'show_notification': True, 'message': 'table %s has no Pay Bill call' % table_number})
        else:
            return redirect('SoReWaApp.views.waiter_manage_tables')


def get_table_total(order):
    try:
        print order
        order_total = 0

        for p in order:
            order_total = order_total+p.product.price
            print order_total
        ###################################
        print 'Total cost is %s' % order_total
        return order_total

    except Order.DoesNotExist:
        return 0


def index(request):
    return render(request, "index.html")


"""def post_on_wall(request):

    if request.method == 'POST':
        if request.POST.get('author_name', '') and request.POST.get('wall_post', ''):
            author_name = request.POST['author_name']
            wall_post = request.POST['wall_post']
            try:
                wall = Wall(author=author_name, post=wall_post)
                wall.save()
            except:
                pass
            pass
"""

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



