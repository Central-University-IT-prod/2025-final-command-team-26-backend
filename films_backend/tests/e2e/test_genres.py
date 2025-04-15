from httpx import Client


def test_1_get_genres():
    print('Получение списка жанров')
    with Client() as client:
        response = client.get(url='http://api:8080/api/genres')
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
