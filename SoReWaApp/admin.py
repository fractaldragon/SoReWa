from django.contrib import admin
from models import Product, Category
# Register your models here.


from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                (image_url, image_url, file_name, _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))





class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_available')
    filter_horizontal = ('products',)


class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'price', 'description', 'is_available', 'image', 'image_tag')
    #readonly_fields = ('image',)






admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
