from django.shortcuts import render

def book_detail(request):
    return render(
        request,
        'single_pages/book_detail.html',
    )


def landing(request):
    return render(
        request,
        'single_pages/landing.html',
    )
