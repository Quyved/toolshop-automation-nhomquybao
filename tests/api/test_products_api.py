"""Sprint 2 - Products API tests."""
import json
from pathlib import Path

import pytest

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text(encoding="utf-8"))


@pytest.mark.api
def test_products_first_page_has_pagination_and_product_shape(api):
    """Goal: contract of GET /products.
    Precondition: none.
    Expected: pagination keys present, data length between 1 and per_page, every product has valid shape."""
    response = api.get("/products", params={"page": 1})
    assert response.status == 200, response.text()
    body = response.json()
    for key in ("current_page", "data", "per_page", "total", "last_page"):
        assert key in body, f"missing key {key}"
    assert 0 < len(body["data"]) <= body["per_page"]
    for product in body["data"]:
        assert isinstance(product["id"], (str, int))
        assert isinstance(product["name"], str) and product["name"].strip()
        assert isinstance(product["price"], (int, float)) and product["price"] > 0


@pytest.mark.api
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_search_api_returns_only_matching_names(api, case):
    """Goal: GET /products/search?q=... filters by name.
    Precondition: search keywords in data/search_keywords.json.
    Expected: at least one result and every name contains the keyword."""
    response = api.get("/products/search", params={"q": case["keyword"]})
    assert response.status == 200, response.text()
    names = [p["name"] for p in response.json()["data"]]
    assert names, f"no results for {case['keyword']}"
    assert all(case["must_contain"] in n.lower() for n in names), names


@pytest.mark.api
@pytest.mark.parametrize("path, expected", [("/users/me", 401), ("/products/does-not-exist", 404)])
def test_protected_or_missing_resource_returns_4xx(api, path, expected):
    """Goal: error handling for protected and missing endpoints.
    Precondition: unauthenticated request.
    Expected: 401 for protected resource, 404 for missing resource."""
    response = api.get(path)
    assert response.status == expected, response.text()
