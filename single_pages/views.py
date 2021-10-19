from django.shortcuts import render

from book.forms import RentalForm
from book.models import Book, Reservation

def index(request):
    recent_books = Book.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/index.html',
        {
            'recent_books': recent_books,
        }
    )

def info(request):
    return render(
        request,
        'single_pages/info.html'
    )

def search(request):
    return render(
        request,
        'single_pages/search.html'
    )
