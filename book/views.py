from django.views.generic import ListView, DetailView

from book.models import Book, Category


class BookList(ListView):
    model = Book;
    order = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BookList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        return context

class BookDetail(DetailView):
    model = Book

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BookDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        return context

