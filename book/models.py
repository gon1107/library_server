from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255, unique=True,allow_unicode=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Book(models.Model):

    title = models.CharField(max_length = 30)
    hook_text = models.CharField(max_length = 100, blank=True)
    book_author = models.CharField(max_length = 128)
    publisher = models.CharField(max_length = 255)
    price = models.IntegerField()
    release_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload =models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}] {self.title} by {self.author}'

    def get_absolute_url(self):
        return f'/book/{self.pk}/'