from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client

from book.models import Book, Category, Tag


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_python = Category.objects.create(name='python', slug='python')

        self.tag_hello = Tag.objects.create(name='hello', slug='hello')
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')

        self.tag_best_seller = Tag.objects.create(name='best seller', slug='best-seller')
        self.tag_new_book = Tag.objects.create(name='new book', slug='new-book')
        self.tag_monthly_best = Tag.objects.create(name='monthly best', slug='monthly-best')
        self.tag_Top10 = Tag.objects.create(name='Top10', slug='Top10')

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

        self.book_001.tags.add(self.tag_hello)
        self.book_001.tags.add(self.tag_best_seller)
        self.book_001.tags.add(self.tag_Top10)

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

        self.book_003.tags.add(self.tag_python_kor)
        self.book_003.tags.add(self.tag_python)
        self.book_003.tags.add(self.tag_new_book)

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
        # document.querySelector("#book-1 > div.col-md-9.col-lg-9 > div > span")
        # # book-1 > div.col-md-9.col-lg-9 > div > span
        # / html / body / div[2] / div / div[1] / div / div / div[1] / div[2] / div / span
        self.assertIn(self.tag_hello.__str__(), book_001_card.text)
        self.assertNotIn(self.tag_python.__str__(), book_001_card.text)
        self.assertNotIn(self.tag_python_kor.__str__(), book_001_card.text)
        # # book-1 > div.col-md-9.col-lg-9 > div > a:nth-child(10) > span
        # document.querySelector("#book-1 > div.col-md-9.col-lg-9 > div > a:nth-child(9) > span")
        # / html / body / div[2] / div / div[1] / div / div / div[1] / div[2] / div / a[1] / span
        self.assertIn(self.tag_best_seller.__str__(), book_001_card.text)
        self.assertIn(self.tag_Top10.__str__(), book_001_card.text)
        self.assertNotIn(self.tag_new_book.__str__(), book_001_card.text)
        self.assertNotIn(self.tag_monthly_best.__str__(), book_001_card.text)

        book_002_card = main_area.find('div', id='book-2')
        self.assertIn(self.book_002.title, book_002_card.text)
        self.assertIn(self.book_002.category.name, book_002_card.text)
        self.assertNotIn(self.tag_hello.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_python.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_python_kor.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_best_seller.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_Top10.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_new_book.__str__(), book_002_card.text)
        self.assertNotIn(self.tag_monthly_best.__str__(), book_002_card.text)

        book_003_card = main_area.find('div', id='book-3')
        self.assertIn(self.book_003.title, book_003_card.text)
        self.assertIn('미분류', book_003_card.text)
        self.assertNotIn(self.tag_hello.__str__(), book_003_card.text)
        self.assertIn(self.tag_python.__str__(), book_003_card.text)
        self.assertIn(self.tag_python_kor.__str__(), book_003_card.text)
        self.assertNotIn(self.tag_best_seller.__str__(), book_003_card.text)
        self.assertNotIn(self.tag_Top10.__str__(), book_003_card.text)
        self.assertIn(self.tag_new_book.__str__(), book_003_card.text)
        self.assertNotIn(self.tag_monthly_best.__str__(), book_003_card.text)
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

        # 2.7. 첫 번째 포스트의 tag.name이 포스트 영역에 있다.
        self.assertIn(self.tag_hello.__str__(), book_area.text)
        self.assertNotIn(self.tag_python.__str__(), book_area.text)
        self.assertNotIn(self.tag_python_kor.__str__(), book_area.text)
        self.assertIn(self.tag_best_seller.__str__(), book_area.text)
        self.assertIn(self.tag_Top10.__str__(), book_area.text)
        self.assertNotIn(self.tag_new_book.__str__(), book_area.text)
        self.assertNotIn(self.tag_monthly_best.__str__(), book_area.text)

    def test_category_page(self):
        # 'programming' 카테고리를 가지는 포스트 글들을 출력하는 페이지로 접속한다.
        # 접속 후 응답 내용들은 response 변수에 저장된다.
        # self.category_programming.get_absolute_url() 함수는 추후 구현해야 한다.
        response = self.client.get(self.category_programming.get_absolute_url())

        # 응답 내용 중 status_code 값을 통해서 페이지가 정상적으로 동작하는지 확인한다.
        self.assertEqual(response.status_code, 200)

        # 응답 내용의 content 변수에 담긴 html 문서를 BeautifulSoup가 구문 분석
        # 분석한 결과를 soup 변수에 저장한다.
        soup = BeautifulSoup(response.content, 'html.parser')

        # 내비게이션 테스트 함수 호출하여 내비게이션 테스트 수행
        self.navbar_test(soup)

        # 카테고리 카드 테스트 함수를 호출하여 카테고리 카드 테스트 수행
        self.category_card_test(soup)

        # 카테고리 페이지 내에 'programming' 카테고리 뱃지가 포함되어 있는지 확인
        self.assertIn(self.category_programming.name, soup.h1.text)

        # 카테고리 페이지 내에 div 태그 중 id가 main-area인 div 태그를 찾는다.
        # 찾은 div 태그 내용을 main_area 변수에 저장한다.
        main_area = soup.find('div', id='main-area')

        # main_area 영역 내에 'programming' 카테고리 뱃지 포함 유무를 체크한다.
        self.assertIn(self.category_programming.name, main_area.text)

        # 첫번째 글의 제목은 main_area에 존재해야 한다
        # (첫 번째 글의 카테고리는 'programming'이므로)
        # 두 번째, 세 번째 글의 제목은 main_area에 존재하면 안 된다.
        # (두 번째, 세 번째 글의 카테고리는 'programming'이 아니므로)
        self.assertIn(self.book_001.title, main_area.text)
        self.assertNotIn(self.book_002.title, main_area.text)
        self.assertNotIn(self.book_003.title, main_area.text)

    # 태그 페이지 테스트
    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.__str__(), soup.h1.text)

        # main-area 내부에는 hello 태그이름과 book_001 글의 타이틀만 존재해야 한다.
        # 나머지는 main-area 내부에 타이틀이 존재하면 안 된다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.__str__(), main_area.text)
        self.assertIn(self.book_001.title, main_area.text)
        self.assertNotIn(self.book_002.title, main_area.text)
        self.assertNotIn(self.book_003.title, main_area.text)

    def test_create_book(self):
        # 로그인하지 않으면 status_code가 200이면 안 된다.
        response = self.client.get('/blog/create_book/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 trump가 로그인을 한다.
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/book/create_book/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 obama로 로그인한다.
        self.client.login(username='obama', password="somepassword")
        response = self.client.get('/book/create_book/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 도서 추가 페이지의 제목이 'Create Book - Library' 이어야 한다.
        self.assertEqual('Create Book - Book', soup.title.text)
        # 도서 추가 페이지에 main-area 영역의 제목은 'Create New Book' 이어야 한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Book', main_area.text)

        # 5. Book 방식으로 글 내용을 작성하고
        # 글 작성 요청을 위한 주소를 기입한다.
        # 첫 번째 파라메터: 클라이언트로부터 요청받을 서버주소
        # 두 번째 파라메터: 서버로 전송할 필드명과 값을 딕셔너리 형태로 작성
        self.client.post(
            '/book/create_book/',
            {
                'title': 'Book Form 만들기',
                'content': 'Book Form 페이지를 만듭시다.',
                'book_author' : 'Biden',
                'publisher' : 'Chosun',
                'price' : 20000,
                'release_date' : '2021-09-15',
            }
        )

        self.assertEqual(Book.objects.count(), 4)
        # 6. last() 함수는포스트 글 중 제일 최근에 작성한
        # 포스트 글 하나를 가져온다.
        last_book = Book.objects.last()
        # 7. 제일 최근에 작성한 글의 제목과 작성자명을 비교한다.
        # 제일 최근에 작성한 글 제목은 5번 주석에 입력했던 title이고,
        # 작성자명은 현재 로그인한 obama이다.
        self.assertEqual(last_book.title, 'Book Form 만들기')
        self.assertEqual(last_book.author.username, 'obama')

