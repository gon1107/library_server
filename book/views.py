from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView

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

class BookCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    fields = ['title', 'hook_text', 'book_author', 'publisher', 'price', 'release_date', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    # form_valid() 함수는 CreateView 클래스에 정의된 form_valid() 함수를 재정의
    # form_valid() 함수의 역할은 필수 입력 값과 제약사항이 지켜졌는지 확인하는 함수
    # 이상이 없다면 클라이언트는 정상적인 결과 페이지를 받게 되고,
    # 이상이 있다면 장고가 작성해준 form 영역에 이상여부를 표시해준다.
    def form_valid(self, form):
        # self.request는 클라이언트가 서버로 요청한 정보를 담고 있는 객체
        # self.request.user는 현재 로그인한 사용자의 정보를 담고 있는 User 객체
        current_user = self.request.user

        # is_authenticated: 현재 사용자가 로그인한 상태이면 True, 아니면 False
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            # form.instance는 클라이언트에서 form을 통해 입력한 내용을 담고 있다.
            # 현재 사용자 정보를 author 필드에 채워 넣어준다. (테스트코드 오류 해결)
            form.instance.author = current_user

            response = super(BookCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')

            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()

                    self.object.tags.add(tag)

            return response
        else:
            # 현재 사용자가 로그아웃 상태일 경우는 목록 페이지로 이동한다.
            # 이동하고자 하는 URL 주소를 redirect() 함수의 파라메터로 넘겨주면 된다.
            return redirect('/book/')

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'hook_text', 'book_author', 'publisher', 'price', 'release_date', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'book/book_update_form.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super(BookUpdate, self).get_context_data()

        if self.object.tags.exists():
            tags_str_list = list()

            for t in self.object.tags.all():
                tags_str_list.append(t.name)

            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(BookUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        current_user = self.request.user


        # form.instance는 클라이언트에서 form을 통해 입력한 내용을 담고 있다.
        # 현재 사용자 정보를 author 필드에 채워 넣어준다. (테스트코드 오류 해결)
        form.instance.author = current_user
        # 먼저 부모 클래스의 form_valid() 함수를 이용하여, 필수값이 잘 입력되었는지 확인
        # form_valid()는 추후 클라이언트로 보낼 response(응답) 내용을 리턴한다.

        response = super(BookUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')

        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()

                self.object.tags.add(tag)

        return response


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
