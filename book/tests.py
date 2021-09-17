from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client

from book.models import Book

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('도서목록', navbar.text)
        self.assertIn('Home', navbar.text)#내용 포함
        self.assertIn('자료검색', navbar.text)
        self.assertIn('도서관안내', navbar.text)

        logo_btn = navbar.find('a', text='Library')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        info_btn = navbar.find('a', text='도서관안내')
        self.assertEqual(info_btn.attrs['href'], '/info/')

        search_btn = navbar.find('a', text='자료검색')
        self.assertEqual(search_btn.attrs['href'], '/search/')

        book_list_btn = navbar.find('a', text='도서목록')
        self.assertEqual(book_list_btn.attrs['href'], '/book/')

    def test_book_list(self):
        # 1.1 포스트 목록 페이지를 가져온다.
        response = self.client.get('/book/')
        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)#(결과값, 비교대상) 내용 일치
        # 1.3 페이지 타이틀은 '도서목록'이다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, '도서목록')
        # 1.4 내비게이션 바가 있다.
        # 1.5 Home, 자료검색, 도서관안내라는 문구가 내비게이션 바에 있다.
        self.navbar_test(soup)
        # 2.1 메인 영역에 게시물이 하나도 없다면
        self.assertEqual(Book.objects.count(), 0)#동일한 test 환경을 위해 새롭게 생성, 배포할 때 대비
        # 2.2 '아직 게시물이 없습니다'라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # 3.1 게시물이 2개를 등록하고 2개가 등록되었는지 체크
        book_001 = Book.objects.create(
            title='첫 번째 책입니다.',
            content='Hello World. We are the world.',
            book_author='Hong Gil Dong',
            publisher = 'Chosun',
            price = 10000,
            release_date = '2021-09-15',
            author = self.user_trump,
         )

        book_002 = Book.objects.create(
            title='두 번째 책입니다.',
            content='1등이 전부는 아니잖아요?',
            book_author='Hong Gil Dong',
            publisher='Chosun',
            price=20000,
            release_date='2021-09-15',
            author=self.user_obama,
        )
        self.assertEqual(Book.objects.count(), 2)

        # 3.2 포스트 목록 페이지를 새로고침하고
        # 메인 영역에 '아직 게시물이 없습니다.'라는 문구는 더 이상 보이지 않는다.

        response = self.client.get('/book/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

# 포스트 상세페이지 포스트
    def test_book_detail(self):
        # 1.1. 포스트가 하나 있다.
        book_001 = Book.objects.create(
            title='첫 번째 책입니다.',
            content='Hello World. We are the world.',
            book_author='Hong Gil Dong',
            publisher='Chosun',
            price=10000,
            release_date='2021-09-15',
            author=self.user_trump,
        )
        # 1.2. 그 포스트의 url은 'blog/1'이다
        self.assertEqual(book_001.get_absolute_url(), '/book/1/')

        # 2. 첫 번째 도서의 상세 페이지 테스트
        # 2.1. 첫 번째 도서의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(book_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2. 도서목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)
        # 2.3. 첫 번째 도서의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(book_001.title, soup.title.text)
        # 2.4. 첫 번째 도서의 제목이 도서 영역에 있다.
        main_area = soup.find('div', id='main-area')
        book_area = main_area.find('div', id='book-area')
        self.assertIn(book_001.title, book_area.text)
        # 2.5. 첫 번째 도서의 내용(content)이 도서 영역에 있다.
        self.assertIn(book_001.content, book_area.text)

