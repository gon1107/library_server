from django.views.generic import ListView, DetailView

from book.models import Book

class BookList(ListView):
    model = Book;
    order = '-pk'

class BookDetail(DetailView):
    model = Book
