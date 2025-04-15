from httpx import Client


def test_1_base_signup():
    print('Базовая регистрация пользователя')
    with Client() as client:
        response = client.post(
            url='http://api:8080/api/auth/basic/register',
            json={'login': 'AuthUser1', 'password': 'AuthPass123'},
        )
        assert response.status_code == 201, response.text
        assert 'token' in response.json()


def test_2_base_login():
    print('Базовый логин пользователя')
    with Client() as client:
        response = client.post(
            url='http://api:8080/api/auth/basic/login',
            json={'login': 'AuthUser1', 'password': 'AuthPass123'},
        )
        assert response.status_code == 200, response.text
        assert 'token' in response.json()


def test_3_signup_existing_user():
    print('Регистрация с уже существующим логином')
    with Client() as client:
        response = client.post(
            url='http://api:8080/api/auth/basic/register',
            json={'login': 'AuthUser1', 'password': 'AuthPass123'},
        )
        assert response.status_code == 409, response.text


def test_4_login_wrong_password():
    print('Логин с неправильным паролем')
    with Client() as client:
        response = client.post(
            url='http://api:8080/api/auth/basic/login',
            json={'login': 'AuthUser1', 'password': 'WrongPass'},
        )
        assert response.status_code == 404, response.text
