from django.shortcuts import render, redirect
from django.http import Http404
from SoReWaApp.models import Category, Product, Table
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
                return render(request, 'table_selector.html', {'error': error})

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
                        print "table number %s assigned" % table_number
                        return redirect('SoReWaApp.views.table')

                except Table.DoesNotExist:
                    print "la mesa no existe"

    return render(request, 'table_selector.html', {'error': error})


def table(request):
    try:
            category = Category.objects.all()

    except Category.DoesNotExist:
        print "No Categories in the database yet."
        return render(request, 'table.html')

    else:
        #show categories and products
        return render(request, 'table.html', {'category_list': category})


def get_products_from_category(request, offset):
    try:
        offset = str(offset)
        print offset
        if len(offset) <= 50:
            category = Category.objects.get(name=offset, is_available=True)
            print category.products.all()
            return render(request, 'products.html', {'products_list': category.products.all()})

    except Category.DoesNotExist:
        print "No Categories in the database yet."
        raise Http404()


