from django.shortcuts import render
from django.http import Http404
from SoReWaApp.models import Category, Product
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


def choose_table(request): #todo cambiar a numero de mesa, validate session
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
   # request.session["table_number"] = "2"
    error = False
    if "table_number" in request.session:
        print " table number: %s" % request.session["table_number"]
    else:
        print"no table_number"
    if 'table_number' in request.GET:
        table_number = request.GET['table_number']
        if not table_number or not (table_number.isdigit()):
            print "error"
            error = True
        else: #todo simplify this
            try:
                category = Category.objects.all()
            except Category.DoesNotExist:
                print "No Categories in the database yet."
                return render(request, 'table.html')
            else:
                #show categories and products
                return render(request, 'table.html', {'category_list': category})
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


