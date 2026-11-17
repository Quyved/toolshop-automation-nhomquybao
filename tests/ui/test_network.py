"""Sprint 2 - Network interception, route mocking, and API + UI integration."""
import json
import re

import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage
from pages.home_page import HomePage

PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {
    "current_page": 1,
    "data": [],
    "from": None,
    "last_page": 1,
    "per_page": 9,
    "to": None,
    "total": 0,
}


@pytest.mark.ui
def test_home_without_images_still_lists_products(page):
    """Goal: verify the homepage renders products correctly when image assets are blocked.
    Precondition: route aborts image file requests.
    Expected: product cards are displayed and at least one image request was intercepted and aborted."""
    blocked = []

    def block(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    assert blocked, "no image request was blocked"


@pytest.mark.ui
def test_home_with_empty_product_list_shows_no_results(page):
    """Goal: verify empty product grid UI state using route response mocking.
    Precondition: list API mocked with EMPTY_PAGE response.
    Expected: 'There are no products found.' message is shown and zero product cards appear."""
    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE)),
    )
    home = HomePage(page).open()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


@pytest.mark.ui
def test_home_when_product_api_fails_page_stays_usable(page):
    """Goal: verify UI resilience when the product API returns an internal server error.
    Precondition: list API mocked to return HTTP 500.
    Expected: zero product cards are rendered but search input remains usable."""
    page.route(PRODUCT_LIST, lambda route: route.fulfill(status=500, body="{}"))
    home = HomePage(page).open()
    expect(home.search_box).to_be_editable()
    expect(home.product_names).to_have_count(0)


@pytest.mark.ui
def test_home_renders_price_from_api_response(page):
    """Goal: verify UI dynamically reflects price values from modified API payload.
    Precondition: real API response fetched and first product price patched to 999.99.
    Expected: first product price element on the page renders as '$999.99'."""

    def patch(route):
        response = route.fetch()
        body = response.json()
        body["data"][0]["price"] = 999.99
        route.fulfill(response=response, json=body)

    page.route(PRODUCT_LIST, patch)
    home = HomePage(page).open()
    expect(home.product_prices.first).to_have_text("$999.99")


@pytest.mark.ui
def test_account_page_with_token_injected_skips_login_form(page, auth_token):
    """Goal: use API-generated auth token to seed browser localStorage and bypass login form.
    Precondition: valid token generated via auth_token fixture.
    Expected: AccountPage opens directly with title 'My account' and user menu displays 'QA Bot'."""
    page.add_init_script(f"window.localStorage.setItem('auth-token', {json.dumps(auth_token)})")
    account = AccountPage(page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")
