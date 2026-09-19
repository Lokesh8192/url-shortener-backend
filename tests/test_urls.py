def test_create_short_url(client):
    response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com"
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["original_url"] == "https://example.com/"
    assert body["short_code"]
    assert body["short_url"]
    assert body["is_active"] is True
    assert body["click_count"] == 0


def test_create_short_url_with_expiration(client):
    response = client.post(
        "/urls",
        json={
            "original_url": "https://example.com",
            "expires_at": "2026-12-31T23:59:59Z",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["expires_at"] is not None


def test_invalid_url(client):
    response = client.post(
        "/urls",
        json={
            "original_url": "not-a-valid-url",
        },
    )

    assert response.status_code == 422