from app.models.product import Product


def test_list_products_empty(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_list_products_returns_seeded_data(client, db_session):
    product = Product(
        name="Test Widget", retailer="walmart", url="https://example.com/1", current_price=9.99
    )
    db_session.add(product)
    db_session.commit()

    response = client.get("/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Test Widget"


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404


def test_filter_products_by_retailer(client, db_session):
    db_session.add_all(
        [
            Product(name="A", retailer="walmart", url="u1", current_price=1.0),
            Product(name="B", retailer="sams_club", url="u2", current_price=2.0),
        ]
    )
    db_session.commit()

    response = client.get("/products", params={"retailer": "walmart"})
    body = response.json()
    assert len(body) == 1
    assert body[0]["retailer"] == "walmart"
