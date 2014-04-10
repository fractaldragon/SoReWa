from django.shortcuts import render
from django.http import Http404
from SoReWaApp.models import Category
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