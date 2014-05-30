from django.db import models
from SoReWa import settings
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=700, blank=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='imgs/', default='imgs/logoSoReWa.jpg', ) #settings.STATIC_URL+

    def image_tag(self):
        return u'<img class="img_thumbnail" src="/media/%s" />' % self.image  # remove /media/ in src if you want to see them in development
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def __unicode__(self):
        return u'$ %s   %s' % (self.price, self.name)


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=700, blank=True)
    products = models.ManyToManyField(Product, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s ' % self.name


class Order(models.Model):
    order_number = models.PositiveIntegerField()
    table_number = models.ForeignKey('Table')
    date = models.DateTimeField(blank=True, null=True)
    sent_to_kitchen = models.BooleanField(default=False)
    product = models.ForeignKey('Product')
    #Select  o.NumeroOrden, sum(p.Precio) from ordenes o  inner join productos p  on  o.idproducto = pidproducto where o.ordennumero = 1 group by o.numeroorden

    def __unicode__(self):
        return u'%s order #:%s %s' % (self.table_number, self.order_number, self.product.name)


class TableOrders(models.Model):
    table_id = models.ForeignKey('Table')
    actual_order = models.ForeignKey('Order')
    is_paid = models.BooleanField(default=False)

    def __unicode__(self):
        return u'table: %s order: %s' % (self.table_id, self.actual_order)


class Table (models.Model):
    number = models.PositiveIntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)
    calls_waiter = models.BooleanField(default=False)
    calls_order = models.BooleanField(default=False)
    calls_bill = models.BooleanField(default=False)

    def __unicode__(self):
        return u'table #:%s ' % self.number




