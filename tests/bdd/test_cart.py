"""BDD step definitions for the search-to-cart shopping flow.

Step definitions only call page objects (no locators here).
Run: pytest tests/bdd -v
"""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

scenarios("cart.feature")


@given("I am on the home page", target_fixture="home")
def open_home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I search for "{keyword}"'))
def search_product(home, keyword):
    home.search(keyword)
    expect(home.search_completed).to_be_visible()


@when(parsers.parse('I open the product "{product}"'), target_fixture="product_page")
def open_product(home, product):
    product_page = home.open_product(product)
    expect(product_page.unit_price).to_be_visible()
    return product_page


@when(parsers.parse("I add it to the cart with quantity {quantity:d}"), target_fixture="unit_price")
def add_to_cart(product_page, quantity):
    unit_price = product_page.price()
    product_page.add_to_cart(quantity=quantity)
    expect(product_page.cart_quantity).to_have_text(str(quantity))
    return unit_price


@when("I view the shopping cart", target_fixture="cart")
def view_cart(product_page):
    cart = product_page.go_to_cart()
    expect(cart.total).to_be_visible()
    return cart


@then(parsers.parse('the cart shows "{product}" with quantity {quantity:d}'))
def cart_shows_product(cart, product, quantity):
    expect(cart.product_titles).to_have_count(1)
    expect(cart.product_titles.first).to_contain_text(product)
    expect(cart.quantities.first).to_have_value(str(quantity))


@then(parsers.parse("the line price equals the unit price times {quantity:d}"))
def line_price_matches(cart, unit_price, quantity):
    expect(cart.line_prices).to_have_count(1)
    assert cart.line_totals() == [pytest.approx(unit_price * quantity)]


@then("the cart total equals the sum of all line prices")
def cart_total_matches(cart):
    assert cart.total_value() == pytest.approx(sum(cart.line_totals()))
