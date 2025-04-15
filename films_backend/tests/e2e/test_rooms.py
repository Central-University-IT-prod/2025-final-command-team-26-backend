from httpx import Client

ROOM_ID = None


def get_token(client):
    response = client.post(
        url='http://api:8080/api/auth/basic/login',
        json={'login': 'RoomUser1', 'password': 'RoomPass123'},
    )
    assert response.status_code == 200, response.text
    return response.json()['token']


def test_1_create_room():
    print('Создание комнаты')
    global ROOM_ID
    with Client() as client:
        client.post(
            url='http://api:8080/api/auth/basic/register',
            json={'login': 'RoomUser1', 'password': 'RoomPass123'},
        )
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/rooms',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Test Room'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == 'Test Room'
        ROOM_ID = response.json()['id']


def test_2_create_room_minimal():
    print('Создание комнаты с минимальными данными')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/rooms',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Minimal Room'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == 'Minimal Room'


def test_3_create_room_no_title():
    print('Ошибка при создании комнаты без title')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/rooms',
            headers={'Authorization': f'Bearer {token}'},
            json={},
        )
        assert response.status_code == 400, response.text


def test_4_create_room_no_auth():
    print('Ошибка при создании комнаты без авторизации')
    with Client() as client:
        response = client.post(
            url='http://api:8080/api/rooms', json={'title': 'No Auth Room'}
        )
        assert response.status_code == 401, response.text


def test_5_create_room_long_title():
    print('Создание комнаты с длинным названием')
    with Client() as client:
        token = get_token(client)
        long_title = 'A' * 255
        response = client.post(
            url='http://api:8080/api/rooms',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': long_title},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == long_title


def test_6_create_second_room():
    print('Создание второй комнаты')
    with Client() as client:
        token = get_token(client)
        response = client.post(
            url='http://api:8080/api/rooms',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Second Room'},
        )
        assert response.status_code == 200, response.text
        assert response.json()['title'] == 'Second Room'
