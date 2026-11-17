"""Sprint 2 - Cart API tests with custom fixture."""
import pytest


@pytest.fixture
def new_cart(api):
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


@pytest.mark.api
def test_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Goal: verify Cart API stores product with requested quantity.
    Precondition: a fresh cart created by new_cart fixture and first available product.
    Expected: cart contains exactly 1 item with quantity 2 and matching product id."""
    product = api.get("/products", params={"page": 1}).json()["data"][0]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product["id"], "quantity": 2})
    assert added.ok, added.text()
    items = api.get(f"/carts/{new_cart}").json()["cart_items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 2
    assert str(items[0]["product_id"]) == str(product["id"])
