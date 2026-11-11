"""Sprint 1 smoke tests for the Toolshop project."""
import re

import pytest
from playwright.sync_api import expect

from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.ui
def test_search_keyword_pliers_shows_matching_products(page):
    """Goal: verify searching for 'pliers' filters the product grid.
    Precondition: none.
    Expected: search caption contains 'pliers' and every displayed product name contains 'pliers'."""
    home = HomePage(page).open().search("pliers")
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")
    names = home.product_names.all_inner_texts()
    assert names, "search returned no products"
    assert all("pliers" in name.lower() for name in names), names


@pytest.mark.smoke
@pytest.mark.ui
def test_cart_add_claw_hammer_quantity_three_updates_badge(page):
    """Goal: verify adding 3 units of 'Claw Hammer' updates the header cart badge.
    Precondition: product 'Claw Hammer' is listed on the home page.
    Expected: cart added toast appears and the cart badge shows '3'."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_have_text("Claw Hammer")
    product.add_to_cart(quantity=3)
    expect(product.toast).to_contain_text("Product added to shopping cart")
    expect(product.cart_quantity).to_have_text("3")


@pytest.mark.smoke
@pytest.mark.ui
def test_login_nonexistent_email_shows_invalid_error(page):
    """Goal: verify login with an unregistered email is rejected.
    Precondition: use a nonexistent email (never test bad passwords on shared accounts).
    Expected: 'Invalid email or password' error appears and URL still ends with /auth/login."""
    login = LoginPage(page).open().login("nobody-here@example.com", "Wrong-Password-123")
    expect(login.error).to_contain_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/auth/login$"))


@pytest.mark.smoke
@pytest.mark.ui
def test_contact_empty_form_shows_required_errors(page):
    """Goal: verify submitting an empty contact form triggers field validation errors.
    Precondition: none.
    Expected: 'Subject is required' and 'Message is required' errors are displayed."""
    contact = ContactPage(page).open().submit()
    expect(contact.errors.filter(has_text="Subject is required")).to_be_visible()
    expect(contact.errors.filter(has_text="Message is required")).to_be_visible()
