def test_create_short_url(client, auth_headers):
    response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    body = response.json()

    assert body["original_url"] == "https://example.com/"
    assert body["short_code"]
    assert body["short_url"]
    assert body["is_active"] is True
    assert body["click_count"] == 0


def test_list_urls(client, auth_headers):
    first_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers
    )

    second_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.org",
        },
        headers=auth_headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get("/urls", headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == 2
    assert body[1]["id"] == 1


def test_get_url_by_id(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers
    )

    assert create_response.status_code == 201

    url_id = create_response.json()["id"]

    response = client.get(
        f"/urls/{url_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == url_id
    assert body["original_url"] == "https://example.com/"


def test_get_url_by_id_not_found(client, auth_headers):
    response = client.get("/urls/9999", headers=auth_headers)

    assert response.status_code == 404

    body = response.json()

    assert body["status"] == "error"
    assert body["message"] == "URL not found"


def test_delete_url(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers
    )

    assert create_response.status_code == 201

    url_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/urls/{url_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    body = delete_response.json()

    assert body["status"] == "success"
    assert body["message"] == "URL deleted successfully"

    get_response = client.get(
        f"/urls/{url_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_url(
    client,
    auth_headers,
):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    url_id = create_response.json()["id"]

    second_user_response = client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "Test@1234",
        },
    )

    assert second_user_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "Test@1234",
        },
    )

    second_token = login_response.json()["access_token"]

    response = client.get(
        f"/urls/{url_id}",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["status"] == "error"
    assert body["message"] == "URL not found"


def test_create_short_url_with_expiration(client, auth_headers):
    response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
            "expires_at": "2026-12-31T23:59:59Z",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["expires_at"] is not None


def test_invalid_url(client, auth_headers):
    response = client.post(
        "/urls",
        json={
            "original_url": "not-a-valid-url",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_redirect_short_url(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com"
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"


def test_click_count_increments(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com"
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    data = create_response.json()
    short_code = data["short_code"]

    first_response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert first_response.status_code == 307

    second_response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert second_response.status_code == 307

    # Fetch the URL again through an API endpoint later
    # once we implement URL management/statistics.


def test_short_code_not_found(client):
    response = client.get(
        "/doesNotExist123",
        follow_redirects=False,
    )

    assert response.status_code == 404

    body = response.json()

    assert body["status"] == "error"
    assert body["message"] == "Short URL isn't found!"


def test_expired_short_url(client, auth_headers):
    response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
            "expires_at": "2020-01-01T00:00:00Z",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    short_code = response.json()["short_code"]

    redirect_response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 410

    body = redirect_response.json()

    assert body["status"] == "error"
    assert body["message"] == "Short URL has expired"
