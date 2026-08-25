def test_signup_creates_user(client):
    response = client.post(
        "/auth/signup", json={"email": "test@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "test@example.com"
    assert "id" in body


def test_signup_duplicate_email_fails(client):
    client.post("/auth/signup", json={"email": "dupe@example.com", "password": "secret123"})
    response = client.post(
        "/auth/signup", json={"email": "dupe@example.com", "password": "other123"}
    )
    assert response.status_code == 400


def test_login_returns_token(client):
    client.post("/auth/signup", json={"email": "login@example.com", "password": "secret123"})
    response = client.post(
        "/auth/login", data={"username": "login@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post("/auth/signup", json={"email": "wrongpw@example.com", "password": "secret123"})
    response = client.post(
        "/auth/login", data={"username": "wrongpw@example.com", "password": "nope"}
    )
    assert response.status_code == 401
