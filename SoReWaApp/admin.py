from django.contrib import admin
from models import Product, Category
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_available')
    filter_horizontal = ('products',)


class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'price', 'description', 'is_available', 'image', 'image_tag')
    #readonly_fields = ('image',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
