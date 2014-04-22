from django.contrib import admin
from models import Product, Category, Table, Order
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_available')
    filter_horizontal = ('products',)


class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'price', 'description', 'is_available', 'image', 'image_tag')
    #readonly_fields = ('image',)


class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'order', 'is_occupied', 'calls_waiter', 'calls_order', 'calls_bill')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'date', 'is_paid', 'total')
    filter_horizontal = ('products_list',)



admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Order, OrderAdmin)

