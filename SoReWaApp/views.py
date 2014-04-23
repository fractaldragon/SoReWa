import datetime
from django.shortcuts import render, redirect
from django.http import Http404
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
                        table_order = Order(table_number=table_number, date=datetime.datetime.now())
                        table_order.save()
                        print "table number %s assigned" % table_number
                        return redirect('SoReWaApp.views.table')

                except Table.DoesNotExist:
                    print "table does not exist"
                    error = True

    return render(request, 'table_selector.html', {'error': error, 'table_list': table_list})


def table(request):
    try:
        #category = Category.objects.all()
        category = Category.objects.filter(is_available=True)

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

                        if len(product_name) <= 100: #todo no dejar quemada la variable del tamanho
                            try:
                                chosen_product = Product.objects.get(name=product_name)
                                session_table.order.products_list.add(chosen_product)

                            except Product.DoesNotExist:
                                print "product does not exist"

                        else:
                            print "Product name too long!"

                    else:
                        print "No product Name"
                else:
                    print"no tengo post"
                    return render(request, 'add_product.html')

            else:
                print "got session but table is NOT occupied"
                del request.session["table_number"]
                return redirect('SoReWaApp.views.choose_table')

        except Table.DoesNotExist:
            print "Table does not exist in the system"
            return redirect('SoReWaApp.views.choose_table')
    else:
        return redirect('SoReWaApp.views.choose_table')



def remove_from_order(request):
    pass


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

