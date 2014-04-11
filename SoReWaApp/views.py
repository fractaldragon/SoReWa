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


def add_product(request):
    pass


def remove_product(request):
    pass


def create_category(request):
    pass


def delete_category(request):
    pass


def edit_category(request):
    pass


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
    """try:

        if 'categoryName' in request.GET:
            print("hay nombre")
            if request.GET['categoryName']:
                category_name = request.GET['categoryName']
                print request.GET['categoryName']
                category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        print "No Categories in the database yet."
        return render(request, 'table.html')

    else:
        return render(request, {'products.html':category.products} )
            """

    try:
        offset = str(offset)
        print offset
        category = Category.objects.get(name=offset)
        print category.products.all()
        return render(request,'products.html', {'products_list': category.products.all()})
    except Category.DoesNotExist:
        print "No Categories in the database yet."
        raise Http404()


