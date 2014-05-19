from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from SoReWaApp.views import table, get_products_from_category, choose_table, add_to_order, view_table_order, remove_from_order, \
    call_order, call_waiter, call_bill, waiter_check_tables, waiter_view_table_order, waiter_remove_product, waiter_manage_tables,\
    get_products, waiter_add_product, waiter_view_table_order_added_product, waiter_attend_waiter_call, waiter_attend_order_call, waiter_attend_pay_call, index
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SoReWa.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', index),
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', logout),

    url(r'^table_number/$', choose_table), #todo if you dont hava table number sends to choose table else to table
    url(r'^table/$', table),
    url(r'^category_products/(\w+)/$', get_products_from_category),
    url(r'^add_product_to_order/$', add_to_order),
    url(r'^remove_product_from_order/$', remove_from_order),
    url(r'^view_table_order/$', view_table_order),
    url(r'^call_waiter/$', call_waiter),
    url(r'^call_order/$', call_order),
    url(r'^call_bill/$', call_bill),
    url(r'^view_tables/$', waiter_check_tables),
    url(r'^table_order/(\d{1,2})/$', waiter_view_table_order),
    url(r'^waiter_remove_product/$', waiter_remove_product),
    url(r'^waiter/$', waiter_manage_tables),
    url(r'^products/$', get_products),
    url(r'^waiter_add_product_to_table/$', waiter_add_product),
    url(r'^waiter_attend_waiter_call/$', waiter_attend_waiter_call),
    url(r'^waiter_attend_order_call/$', waiter_attend_order_call),
    url(r'^waiter_attend_pay_call/$', waiter_attend_pay_call),


    url(r'^waiter_add_product_to_table/SoReWaApp.views.waiter_view_table_order/$', waiter_view_table_order_added_product),
    url(r'^waiter_remove_product/SoReWaApp.views.waiter_view_table_order/$', waiter_view_table_order_added_product),



)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)