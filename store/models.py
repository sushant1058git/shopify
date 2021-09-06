from django.db import models
from category.models import Category
from django.urls import reverse

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    product_description = models.TextField(blank=True, max_length=200)
    price = models.FloatField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_details', args= [self.category.slug,self.slug])

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colour(self):
        return super(VariationManager, self).filter(variation_category='colour', is_active=True)

    def size(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice=[
    ('colour', 'colour'),
    ('size', 'size')
]


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
