from django.db import models
from SoReWa import settings
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=700, blank=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to=settings.STATIC_URL+'imgs/', default=settings.STATIC_URL+'imgs/logoSoReWa.jpg', )

    def image_tag(self):
        return u'<img src="%s" />' % self.image
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




