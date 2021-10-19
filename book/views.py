from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.core.mail import EmailMessage

from book.forms import ReviewForm, RentalForm, ReservationForm
from book.models import Book, Category, Tag, Review, Rental, Reservation


class BookList(ListView):
    model = Book
    order = '-pk'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BookList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        # context['rental'] = Book.objects.get(pk=self.request.POST.get()).rental_set.all()
        return context

class BookDetail(DetailView):
    model = Book

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BookDetail, self).get_context_data()
        reservation = Book.objects.get(pk=self.kwargs['pk']).reservation_set.get(customer=self.request.user)
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        context['rental'] = Book.objects.get(pk=self.kwargs['pk']).rental_set.all().first()
        context['reservation'] = reservation
        context['review_form'] = ReviewForm
        context['rental_form'] = RentalForm
        context['reservation_form'] = ReservationForm
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
                    slug = slugify(t, allow_unicode=True)

                    if len(slug):
                        pass
                    else:
                        return redirect('/book/create_book/?error=true')

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

                slug = slugify(t, allow_unicode=True)

                if len(slug):
                    pass
                else:
                    return redirect(f'/book/update_book/{self.object.pk}?error=true')

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
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_book_count': Book.objects.filter(category=None).count(),
        }
    )

def new_review(request, pk):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, pk=pk)

        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.book = book
                review.author = request.user

                # 우리가 만든 별점 버튼을 이용해서 받은 별점을 review의 score
                # 필드에 저장
                review.score = request.POST.get('my_score')
                review.save()
                return redirect(review.get_absolute_url())
            else:
                return redirect(book.get_absolute_url())
        else:
            raise PermissionDenied

class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(ReviewUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        # current_user = self.request.user
        # form.instance.author = current_user

        response = super(ReviewUpdate, self).form_valid(form)

        my_score = self.request.POST.get('my_score')

        if my_score and (0 < int(my_score) <= 5):
            self.object.score = my_score
            self.object.save()
        else:
            raise ValueError('별점은 1~5 점을 입력하셔야 합니다.')

        return response

def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    book = review.book
    if request.user.is_authenticated and request.user == review.author:
        review.delete()
        return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied

class BookSearch(BookList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        book_list = Book.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()# distinct() 중복 제거
        return book_list

    def get_context_data(self, **kwargs):
        context = super(BookSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context

class RentalCreate(UserPassesTestMixin, CreateView):
    model = Rental
    form_class = RentalForm
    # 'book', 'librarian',
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user

        super(RentalCreate, self).form_valid(form)

        pk = self.kwargs['pk']

        if current_user.is_staff or current_user.is_superuser:

            customer = User.objects.filter(username=self.request.POST.get('customer_str')).first()

            if customer:
                self.object.book = Book.objects.get(pk=pk)

                self.object.librarian = current_user
                self.object.customer = customer
                self.object.save()
            else:
                raise ValueError('없는 고객입니다.')

        return redirect(f'/book/{pk}/')

def delete_rental(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    book = rental.book
    if request.user.is_staff or request.user.is_superuser:
        rental.delete()
        return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied

def new_reservation(request, pk):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, pk=pk)
        rental = book.rental_set.all().first()
        today = datetime.today()

        if request.method == 'POST':
            reservation_form = ReservationForm(request.POST)
            if reservation_form.is_valid():
                reservation = reservation_form.save(commit=False)
                reservation.book = book
                reservation.customer = request.user

                reservation.save()
                reservation_book_count = book.reservation_set.all().count()

                format = '%Y년-%m월-%d일'
                text = '대출 예약이 완료되었습니다.\n'

                if reservation_book_count > 1:
                    text += '이전 대출예약자가 존재합니다.\n 대출예약 대기번호 ' + str(reservation_book_count) + '번입니다.\n'

                if rental:
                    text += '대출 가능 일자는' + datetime.strftime(rental.return_date + timedelta(1), format) + '입니다.'
                else:
                    text += '대출 가능 일자는' + datetime.strftime(today, format) + '입니다.'

                email = EmailMessage(
                    '대출예약완료',
                    text,
                    'kngon1107@gmail.com',
                    ['kngon1107@gmail.com'],
                )
                email.send()
                return render(
                    request,
                    'book/reservation.html',
                    {
                        # 'reservation': reservation,
                        'rental': rental,
                        'today': today,
                        'reservation_book_count': reservation_book_count,
                        'redirect': book.get_absolute_url()
                    }
                )
            else:
                return redirect(book.get_absolute_url())
        else:
            raise PermissionDenied

def delete_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    book = reservation.book
    if reservation.customer == request.user:
        reservation.delete()
        return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied

def change_rental(request, pk):
    book = get_object_or_404(Book, pk=pk)
    rental = book.rental_set.all().first()
    reservations = book.reservation_set.all()

    if rental and (request.user.is_staff or request.user.is_superuser):
        rental.delete()
    else:
        raise PermissionDenied

    if request.method == 'POST':
        rental_form = RentalForm(request.POST)
        if rental_form.is_valid():
            rental = rental_form.save(commit=False)
            rental.book = book
            rental.librarian = request.user
            print("*****************" + request.POST.get('reservation_pk'))
            rental.customer = User.objects.get(pk=int(request.POST.get('reservation_pk')))
            rental.save()

            for r in reservations:
                if rental.customer == r.customer:
                    rental_text = '대출이 완료되었습니다.'

                    rental_email = EmailMessage(
                        '대출완료',
                        rental_text,
                        'kngon1107@gmail.com',
                        ['kngon1107@gmail.com'],
                    )
                    rental_email.send()
                else:
                    cancel_text = '대출 예약이 취소되었습니다.'

                    cancel_email = EmailMessage(
                        '대출예약취소',
                        cancel_text,
                        'kngon1107@gmail.com',
                        [r.customer.email],
                    )
                    cancel_email.send()
                r.delete()

            return render(
                request,
                'book/reservation_list.html',
                {
                    # 'reservation': reservation,
                    'rental': rental,
                    'redirect': book.get_absolute_url()
                }
            )
        else:
            return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied
    return redirect(book.get_absolute_url())

def reservation_list(request):
    reservations = Reservation.objects.all()

    return render(
        request,
        'book/reservation_list.html',
        {
            'reservations': reservations,
            'rental_form': RentalForm,
        }
    )
# class ReservationCreate(LoginRequiredMixin, CreateView):
#     model = Reservation
#     template_name = 'book/reservation.html'
#
#     def dispatch(self, request, *args, **kwargs):
#         pk = self.kwargs['pk']
#         if request.user.is_authenticated and request.user == self.get_object().author:
#             return super(ReservationCreate, self).dispatch(request, *args, **kwargs)
#         else:
#             raise PermissionDenied
#
#     def form_valid(self, form):
#         current_user = self.request.user
#         pk = self.kwargs['pk']
#         response = super(ReservationCreate, self).form_valid(form)
#
#         if current_user.is_authenticated:
#             customer = current_user
#
#             if customer:
#                 self.object.book = Book.objects.get(pk=pk)
#                 self.object.customer = customer
#                 self.object.save()
#             else:
#                 raise ValueError('error')
#         else:
#             return redirect(f'/book/{pk}/')
#         return response

# def rental_page(request, pk):
#     rental = Rental.objects.get(pk=pk)
#
#     book_list = Book.objects.all()
#
#     return render(
#         request,
#         'book/book_list.html',
#         {
#             'book_list': book_list,
#             'rental': rental,
#             'categories': Category.objects.all(),
#             'no_category_book_count': Book.objects.filter(category=None).count(),
#         }
#     )
