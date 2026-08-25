from app.models.product import Product


def _signup_and_login(client, email="alertuser@example.com", password="secret123"):
    client.post("/auth/signup", json={"email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_alert_requires_auth(client, db_session):
    product = Product(name="A", retailer="walmart", url="u1", current_price=10.0)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.post("/alerts", json={"product_id": product.id, "target_price": 5.0})
    assert response.status_code == 401


def test_create_alert_success(client, db_session):
    product = Product(name="A", retailer="walmart", url="u1", current_price=10.0)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    headers = _signup_and_login(client)
    response = client.post(
        "/alerts", json={"product_id": product.id, "target_price": 5.0}, headers=headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["target_price"] == 5.0
    assert body["is_triggered"] is False


def test_list_alerts_only_returns_own(client, db_session):
    product = Product(name="A", retailer="walmart", url="u1", current_price=10.0)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    headers = _signup_and_login(client)
    client.post("/alerts", json={"product_id": product.id, "target_price": 5.0}, headers=headers)

    response = client.get("/alerts", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
