from tests.conftest import auth_header


async def _genre(client, admin_header, name="Science Fiction", slug="science-fiction"):
    response = await client.post(
        "/api/genres", json={"name": name, "slug": slug}, headers=admin_header
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _platform(client, admin_header):
    response = await client.post(
        "/api/platforms",
        json={"name": "Example Stream", "slug": "example-stream", "website_url": "https://example.test"},
        headers=admin_header,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _title(client, admin_header, genre_id, platform_id, published=True):
    response = await client.post(
        "/api/titles",
        json={
            "name": "Orbit", "content_type": "movie", "release_year": 2025,
            "synopsis": "A science-fiction test title.", "genre_ids": [genre_id],
            "platform_ids": [platform_id], "is_published": published,
        },
        headers=admin_header,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_catalog_discovery_filters_and_admin_write(client, admin_token):
    header = auth_header(admin_token)
    genre = await _genre(client, header)
    platform = await _platform(client, header)
    title = await _title(client, header, genre["id"], platform["id"])

    listing = await client.get("/api/titles?q=orbit&genre=science-fiction&platform=example-stream&sort_by=name&sort_order=asc")
    assert listing.status_code == 200
    assert listing.json()["meta"] == {"offset": 0, "limit": 20, "total": 1}
    assert listing.json()["data"][0]["id"] == title["id"]
    assert (await client.get(f"/api/titles/{title['id']}")).json()["platforms"][0]["slug"] == "example-stream"

    updated = await client.patch(
        f"/api/titles/{title['id']}", json={"is_published": False}, headers=header
    )
    assert updated.status_code == 200
    assert (await client.get(f"/api/titles/{title['id']}")).status_code == 404


async def test_watchlist_and_favorites_are_private(client, user_token, admin_token):
    admin_header = auth_header(admin_token)
    genre = await _genre(client, admin_header)
    platform = await _platform(client, admin_header)
    title = await _title(client, admin_header, genre["id"], platform["id"])
    user_header = auth_header(user_token)

    added = await client.put(f"/api/users/me/watchlist/{title['id']}", headers=user_header)
    assert added.status_code == 201
    assert added.json()["is_favorite"] is False
    favorite = await client.patch(
        f"/api/users/me/watchlist/{title['id']}", json={"is_favorite": True}, headers=user_header
    )
    assert favorite.status_code == 200
    assert (await client.get("/api/users/me/favorites", headers=user_header)).json()["meta"]["total"] == 1
    assert (await client.delete(f"/api/users/me/watchlist/{title['id']}", headers=user_header)).status_code == 204
    assert (await client.get("/api/users/me/watchlist", headers=user_header)).json()["meta"]["total"] == 0


async def test_catalog_validation_and_readiness(client, admin_token):
    header = auth_header(admin_token)
    invalid = await client.post("/api/titles", json={"name": "No type"}, headers=header)
    assert invalid.status_code == 422
    # The test client bypasses application lifespan; readiness still verifies its overridden DB.
    ready = await client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["checks"]["database"] == "ok"
