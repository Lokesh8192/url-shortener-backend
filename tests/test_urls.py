from app.models.url_click import URLClick
from app.models.url import URL
from pathlib import Path


def test_url_click_migration_uses_ip_address_column():
    migration_path = Path(__file__).resolve().parent.parent / "alembic" / "versions" / "26ea792410cf_add_url_click_analytics.py"
    migration_source = migration_path.read_text(encoding="utf-8")

    assert "ip_address" in migration_source
    assert "id_address" not in migration_source


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


def test_update_url(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={"original_url": "https://example.com"},
        headers=auth_headers,
    )
    url_id = create_response.json()["id"]

    response = client.patch(
        f"/urls/{url_id}",
        json={
            "original_url": "https://example.org/path",
            "is_active": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["original_url"] == "https://example.org/path"
    assert body["is_active"] is False


def test_update_url_can_clear_expiration(client, auth_headers):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
            "expires_at": "2026-12-31T23:59:59Z",
        },
        headers=auth_headers,
    )
    url_id = create_response.json()["id"]

    response = client.patch(
        f"/urls/{url_id}",
        json={"expires_at": None},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["expires_at"] is None


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


def test_redirect_records_click_event(
    client,
    auth_headers,
    db_session,
):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    data = create_response.json()

    url_id = data["id"]
    short_code = data["short_code"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 307

    click = (
        db_session.query(URLClick)
        .filter(URLClick.url_id == url_id)
        .first()
    )

    assert click is not None
    assert click.clicked_at is not None


def test_redirect_increments_click_count(
    client,
    auth_headers,
    db_session,
):
    create_response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    data = create_response.json()

    url_id = data["id"]
    short_code = data["short_code"]

    client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    url = db_session.get(
        URL,
        url_id,
    )

    assert url is not None
    assert url.click_count == 2


def test_get_url_stats(
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

    data = create_response.json()

    url_id = data["id"]
    short_code = data["short_code"]

    client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    response = client.get(
        f"/urls/{url_id}/stats",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["url_id"] == url_id
    assert body["short_code"] == short_code
    assert body["total_clicks"] == 2
    assert body["last_clicked_at"] is not None


def test_user_cannot_view_another_users_url_stats(
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

    second_user = client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "Test@1234",
        },
    )

    assert second_user.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "Test@1234",
        },
    )

    second_token = login_response.json()["access_token"]

    response = client.get(
        f"/urls/{url_id}/stats",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["status"] == "error"
    assert body["message"] == "URL not found"
