from django.db import models
from SoReWa import settings
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=700, blank=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='imgs/', default=settings.STATIC_URL+'imgs/logoSoReWa.jpg', )

    def image_tag(self):
        return u'<img class="img_thumbnail" src="%s" />' % self.image
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def __unicode__(self):
        return u'%s' % self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=700, blank=True)
    products = models.ManyToManyField(Product, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s ' % self.name


class Order(models.Model):
    table_number = models.PositiveIntegerField()
    date = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    products_list = models.ManyToManyField(Product, blank=True, null=True)
    total = models.FloatField(default=0.0)

    def __unicode__(self):
        return u'%s' % self.table_number


class Table (models.Model):
    number = models.PositiveIntegerField(unique=True)
    order = models.ForeignKey(Order, blank=True, null=True)
    is_occupied = models.BooleanField(default=False)
    calls_waiter = models.BooleanField(default=False)
    calls_order = models.BooleanField(default=False)
    calls_bill = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s ' % self.number

