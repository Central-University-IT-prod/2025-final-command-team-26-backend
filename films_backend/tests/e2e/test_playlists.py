from httpx import Client

PLAYLIST_ID = None
FILM_ID = None


def get_token(client):
    response = client.post(
        url='http://api:8080/api/auth/basic/login',
        json={'login': 'PlaylistUser1', 'password': 'PlaylistPass123'},
    )
    assert response.status_code == 200, response.text
    return response.json()['token']


def test_1_create_playlist():
    print('Создание плейлиста')
    global PLAYLIST_ID
    with Client() as client:
        client.post(
            url='http://api:8080/api/auth/basic/register',
            json={'login': 'PlaylistUser1', 'password': 'PlaylistPass123'},
        )
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/playlists',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Test Playlist', 'films': []},
        )
        assert response.status_code == 201, response.text
        assert response.json()['title'] == 'Test Playlist'
        PLAYLIST_ID = response.json()['id']


def test_2_create_playlist_with_film():
    print('Создание плейлиста с фильмом')
    global FILM_ID
    with Client() as client:
        token = get_token(client)
        film_response = client.post(
            url='http://api:8080/api/user/films',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Playlist Movie', 'year': 2023, 'genres': []},
        )
        assert film_response.status_code == 201, film_response.text
        FILM_ID = film_response.json()['id']

        response = client.post(
            url='http://api:8080/api/playlists',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Playlist With Film', 'films': [FILM_ID]},
        )
        assert response.status_code == 201, response.text
        assert response.json()['title'] == 'Playlist With Film'
        assert FILM_ID in [film['id'] for film in response.json()['films']]


def test_3_create_playlist_no_title():
    print('Ошибка при создании плейлиста без title')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/playlists',
            headers={'Authorization': f'Bearer {token}'},
            json={'films': []},
        )
        assert response.status_code == 400, response.text


def test_4_create_playlist_empty_title():
    print('Ошибка при создании плейлиста с пустым title')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/playlists',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': '', 'films': []},
        )
        assert response.status_code == 400, response.text


def test_5_list_playlists():
    print('Получение списка плейлистов')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/playlists',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0


def test_6_list_playlists_with_limit():
    print('Получение списка плейлистов с лимитом')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/playlists?limit=1',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1


def test_7_get_playlist():
    print('Получение конкретного плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['id'] == PLAYLIST_ID


def test_8_get_nonexistent_playlist():
    print('Ошибка при получении несуществующего плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.get(
            url='http://api:8080/api/playlists/00000000-0000-0000-0000-000000000000',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 404, response.text


def test_9_update_playlist():
    print('Обновление плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.patch(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Updated Playlist'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == 'Updated Playlist'


def test_10_update_playlist_empty_title():
    print('Ошибка при обновлении плейлиста с пустым title')
    with Client() as client:
        token = get_token(client)
        response = client.patch(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': ''},
        )
        assert response.status_code == 400, response.text


def test_11_add_film_to_playlist():
    print('Добавление фильма в плейлист')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}/films',
            headers={'Authorization': f'Bearer {token}'},
            json={'film_id': FILM_ID},
        )
        assert response.status_code == 200, response.text
        assert FILM_ID in [film['id'] for film in response.json()['films']]


def test_12_add_nonexistent_film_to_playlist():
    print('Ошибка при добавлении несуществующего фильма в плейлист')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}/films',
            headers={'Authorization': f'Bearer {token}'},
            json={'film_id': '00000000-0000-0000-0000-000000000000'},
        )
        assert response.status_code == 404, response.text


def test_13_add_film_to_playlist_no_film_id():
    print('Ошибка при добавлении фильма без film_id')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}/films',
            headers={'Authorization': f'Bearer {token}'},
            json={},
        )
        assert response.status_code == 400, response.text


def test_14_remove_film_from_playlist():
    print('Удаление фильма из плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}/films/{FILM_ID}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 204, response.text


def test_15_remove_nonexistent_film_from_playlist():
    print('Ошибка при удалении несуществующего фильма из плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}/films/00000000-0000-0000-0000-000000000000',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 404, response.text


def test_16_delete_playlist():
    print('Удаление плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url=f'http://api:8080/api/playlists/{PLAYLIST_ID}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 204, response.text


def test_17_delete_nonexistent_playlist():
    print('Ошибка при удалении несуществующего плейлиста')
    with Client() as client:
        token = get_token(client)
        response = client.delete(
            url='http://api:8080/api/playlists/00000000-0000-0000-0000-000000000000',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 404, response.text
