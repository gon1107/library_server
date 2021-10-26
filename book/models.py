# from datetime import timedelta

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return '#' + self.name

    def get_absolute_url(self):
        return f'/book/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/book/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'

class Book(models.Model):

    title = models.CharField(max_length = 30)
    hook_text = models.CharField(max_length = 100, blank=True)
    book_author = models.CharField(max_length = 128)
    publisher = models.CharField(max_length = 255)
    price = models.IntegerField()
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='book/images/%Y/%m/%d/', blank=True)
    file_upload =models.FileField(upload_to='book/files/%Y/%m/%d/', blank=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    # 태그 필드 추가: 다대다 관계는 ManyToManyField 사용
    # 일대다 관계일 때 ForeignKey 사용하는 것과 비교해서 볼 것
    # 다대다 관계라서 속성명 접미사 s
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.title} by {self.author}'

    def get_absolute_url(self):
        return f'/book/{self.pk}/'

    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/331/f34cd00c7f82e89e/svg/{self.author.email}'

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    parent_id = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None) # 자기참조

    def __str__(self):
        return f'{self.author}::{self.score}::{self.content}'

    def get_absolute_url(self):
        return f'{self.book.get_absolute_url()}#review-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/331/f34cd00c7f82e89e/svg/{self.author.email}'

    def get_child_reviews(self):
        reviews = Review.objects.filter(parent_id=self.pk)
        return reviews

class Rental(models.Model):
    book = models.ForeignKey(Book, blank=False, null=True, on_delete=models.SET_NULL)
    librarian = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL, related_name='librarian')
    customer = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL, related_name='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    #default=created_at + timedelta(14)

    def __str__(self):
        return f'{self.pk}. {self.book.title}::{self.librarian}::{self.customer}'

    def get_absolute_url(self):
        return f'{self.book.get_absolute_url()}#rental-{self.pk}'

class Reservation(models.Model):
    book = models.ForeignKey(Book, blank=False, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}. {self.book.title}::{self.customer}'

    def get_absolute_url(self):
        return f'{self.book.get_absolute_url()}#reservation-{self.pk}'


