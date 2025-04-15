from httpx import Client


def test_ping() -> None:
    print('Запуск первого теста')

    with Client() as client:
        response = client.get('http://api:8080/ping')

        assert response.status_code == 200, response.json()
