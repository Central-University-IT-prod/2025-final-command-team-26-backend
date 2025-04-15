from httpx import Client

FILM_ID = None


def get_token(client):
    response = client.post(
        url='http://api:8080/api/auth/basic/login',
        json={'login': 'FilmUser1', 'password': 'FilmPass123'},
    )
    assert response.status_code == 200, response.text
    return response.json()['token']


def test_1_create_film():
    print('Создание фильма')
    global FILM_ID
    with Client() as client:
        client.post(
            url='http://api:8080/api/auth/basic/register',
            json={'login': 'FilmUser1', 'password': 'FilmPass123'},
        )
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Movie',
                'year': 2023,
                'genres': [],
                'note': 'Test note',
                'link': 'https://test.com',
                'tmdb_id': 12345,
            },
        )
        assert response.status_code == 201, response.text
        assert response.json()['title'] == 'Test Movie'
        FILM_ID = response.json()['id']


def test_2_create_film_minimal():
    print('Создание фильма с минимальными данными')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Minimal Movie',
                'genres': [],
            },
        )
        assert response.status_code == 201, response.text
        assert response.json()['title'] == 'Minimal Movie'


def test_3_create_film_no_title():
    print('Ошибка при создании фильма без title')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
            json={'year': 2023},
        )
        assert response.status_code == 400, response.text


def test_4_create_film_invalid_link():
    print('Ошибка при создании фильма с некорректным link')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Invalid Link Movie', 'link': 'invalid_url'},
        )
        assert response.status_code == 400, response.text


def test_5_list_films():
    print('Получение списка фильмов')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0


def test_6_list_films_by_year():
    print('Получение списка фильмов с фильтром по году')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/user/films?years_from=2020&years_to=2025',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)


def test_7_list_films_by_viewed():
    print('Получение списка фильмов с фильтром по статусу просмотра')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/user/films?is_viewed=false',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)


def test_8_get_film():
    print('Получение конкретного фильма')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url=f'http://api:8080/api/user/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['id'] == FILM_ID


def test_9_get_nonexistent_film():
    print('Ошибка при получении несуществующего фильма')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/user/films/00000000-0000-0000-0000-000000000000',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 404, response.text


def test_10_update_film_title():
    print('Обновление фильма - изменение title')
    with Client() as client:
        token = get_token(client)
        response = client.patch(
            url=f'http://api:8080/api/user/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Updated Movie'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == 'Updated Movie'


def test_11_update_film_year():
    print('Обновление фильма - изменение year')
    with Client() as client:
        token = get_token(client)
        response = client.patch(
            url=f'http://api:8080/api/user/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
            json={'year': 2024},
        )
        assert response.status_code == 200, response.text
        assert response.json()['year'] == 2024


def test_12_update_film_empty_title():
    print('Ошибка при обновлении фильма с пустым title')
    with Client() as client:
        token = get_token(client)
        response = client.patch(
            url=f'http://api:8080/api/user/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': ''},
        )
        assert response.status_code == 400, response.text


def test_13_change_view_status_true():
    print('Смена статуса просмотра на True')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/user/films/{FILM_ID}/view',
            headers={'Authorization': f'Bearer {token}'},
            json={'is_viewed': True},
        )
        assert response.status_code == 200, response.text
        assert response.json()['is_viewed'] is True


def test_14_change_view_status_false():
    print('Смена статуса просмотра на False')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/user/films/{FILM_ID}/view',
            headers={'Authorization': f'Bearer {token}'},
            json={'is_viewed': False},
        )
        assert response.status_code == 200, response.text
        assert response.json()['is_viewed'] is False


def test_15_change_view_status_no_field():
    print('Ошибка при смене статуса без поля is_viewed')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/user/films/{FILM_ID}/view',
            headers={'Authorization': f'Bearer {token}'},
            json={},
        )
        assert response.status_code == 400, response.text


def test_16_delete_film():
    print('Удаление фильма')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url=f'http://api:8080/api/user/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 204, response.text


def test_17_delete_nonexistent_film():
    print('Ошибка при удалении несуществующего фильма')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url='http://api:8080/api/user/films/00000000-0000-0000-0000-000000000000',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 404, response.text


def test_18_search_film_no_search():
    print('Ошибка при поиске без search')
    with Client() as client:
        response = client.get(url='http://api:8080/api/user/films/search/film')
        assert response.status_code == 400, response.text
