from django.conf.urls import patterns, include, url
from SoReWaApp.views import table, get_products_from_category, choose_table, add_to_order, view_table_order, remove_from_order, \
    call_order, call_waiter, call_bill
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SoReWa.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^table_number/$', choose_table), #todo if you dont hava table number sends to choose table else to table
    url(r'^table/$', table),
    url(r'^category_products/(\w+)/$', get_products_from_category),
    url(r'^add_product_to_order/$', add_to_order),
    url(r'^remove_product_from_order/$', remove_from_order),
    url(r'view_table_order/$', view_table_order),
    url(r'^call_waiter/$', call_waiter),
    url(r'^call_order/$', call_order),
    url(r'^call_bill/$', call_bill),


)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)