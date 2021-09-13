from django.shortcuts import render

def about_me(request):
    return render(
        request,
        'single_pages/about_me.html',
    )


def index(request):
    return render(
        request,
        'single_pages/index.html',
    )
