from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client

from book.models import Book, Category

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_python = Category.objects.create(name='python', slug='python')

        self.book_001 = Book.objects.create(
            title='첫 번째 책입니다.',
            content='Hello World. We are the world.',
            book_author='Hong Gil Dong',
            publisher='Chosun',
            price=10000,
            release_date='2021-09-15',
            category=self.category_programming,
            author=self.user_trump,
        )

        self.book_002 = Book.objects.create(
            title='두 번째 책입니다.',
            content='1등이 전부는 아니잖아요?',
            book_author='Hong Gil Dong',
            publisher='Chosun',
            price=20000,
            release_date='2021-09-15',
            category=self.category_python,
            author=self.user_obama,
        )
        self.book_003 = Book.objects.create(
            title='세 번째 책입니다.',
            content='category가 없을 수도 있죠',
            book_author='Hong Gil Dong',
            publisher='Chosun',
            price=20000,
            release_date='2021-09-15',
            author=self.user_obama,
        )

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

    # 카테고리 카드영역 테스트
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.book_set.count()})',
                      categories_card.text)
        self.assertIn(f'{self.category_python.name} ({self.category_python.book_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_book_list(self):
        self.assertEqual(Book.objects.count(), 3)

        response = self.client.get('/book/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        book_001_card = main_area.find('div', id='book-1')
        self.assertIn(self.book_001.title, book_001_card.text)
        self.assertIn(self.book_001.category.name, book_001_card.text)

        book_002_card = main_area.find('div', id='book-2')
        self.assertIn(self.book_002.title, book_002_card.text)
        self.assertIn(self.book_002.category.name, book_002_card.text)

        book_003_card = main_area.find('div', id='book-3')
        self.assertIn(self.book_003.title, book_003_card.text)
        self.assertIn('미분류', book_003_card.text)

        # 포스트가 없는 경우

        Book.objects.all().delete()
        self.assertEqual(Book.objects.count(), 0)
        response = self.client.get('/book/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    # 포스트 상세페이지 포스트
    def test_book_detail(self):
        # 1.2. 그 포스트의 url은 'book/1'이다
        # 1.1. 포스트가 하나 있다.
        # 포스트 글은 이미 setUp 함수에 작성된 상태이다.

        # 1.2. 그 포스트의 url은 'book/1'이다
        self.assertEqual(self.book_001.get_absolute_url(), '/book/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1. 첫 번재 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.book_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2. 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)
        # 2.2.1 포스트 우측 카테고리 카드가 있다.
        self.category_card_test(soup)

        # 2.3. 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.book_001.title, soup.title.text)
        # 2.4. 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        book_area = main_area.find('div', id='book-area')
        self.assertIn(self.book_001.title, book_area.text)
        self.assertIn(self.category_programming.name, book_area.text)

        # 2.6. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.book_001.content, book_area.text)