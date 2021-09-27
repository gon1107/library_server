from django.shortcuts import render
from django.views.generic import ListView, DetailView

from book.models import Book, Category, Tag

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

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        book_list = Book.objects.filter(category=None)
    else:
    # URL을 통해서 전달받은 slug 변수를 이용하여
    # Category 테이블을 조회한다.
    # 예) slug 값이 'programming'이면 Category 테이블에서 slug 값이 'programming'인
    # 'programming' 카테고리 객체를 가져와 Category 변수에 담는다.
        category = Category.objects.get(slug=slug)
        book_list = Book.objects.filter(category=category)

    # FBV 방식은 render 함수를 통해 템플릿으로 변수값들을 전달한다.
    # (CBV 방식의 get_conetext_data() 함수와 비교해보세요.)
    # 첫 번째 파라메터: 클라이언트로부터 요청받은 request 변수를 그대로 전달
    # 두 번째 파라메터: 템플릿 경로
    # 세 번째 파라메터: 딕셔너리(Dictionary) 형태로 '변수명':변수값을 작성한다.
    # 세 번째 파라메터 내용이 두 번째 파라메터로 지정한 템플릿으로 전달하게 된다.
    return render(
        request,
        'book/book_list.html',
        {
            'book_list': book_list,
            'category': category,
            'categories': Category.objects.all(),
            'no_category_book_count': Book.objects.filter(category=None).count(),
        }
    )

def tag_page(request, slug):
    # URL 주소로 전달받은 slug 값을 이용하여 Tag 테이블을 검색한다.
    # 예) slug 값이 hello일 경우는 Tag 테이블에서 slug가 hello인 태그를 찾고
    # 찾은 태그를 객체하해서 tag 변수에 저장
    tag = Tag.objects.get(slug=slug)
    # tag 변수에 담긴 태그 객체를 가지는 Book들을 불러와서 book_list 변수에 담는다.
    book_list = tag.book_set.all()

    # 템플릿은 book_list.html 사용
    # 글 목록은 위에서 작성한 book_list 변수에 담겨 있고,
    # 템플릿에 넘길 때 book_list 변수로 넘긴다.
    # tag는 현재 화면에 보이는 태그 페이지의 태그 이름
    # categories는 카테고리 카드에 사용하기 위한 변수
    # no_category_book_count는 카테고리를 가지지 않은 포스트의 수
    return render(
        request,
        'book/book_list.html',
        {
            'book_list': book_list,
            'tag':tag,
            'categories': Category.objects.all(),
            'no_category_book_count': Book.objects.filter(category=None).count(),
        }
    )
