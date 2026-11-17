"""Sprint 2 - Functional UI tests covering all 6 functional groups."""
import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


# --- Group 1: Danh sách và tìm kiếm ---
@pytest.mark.ui
def test_search_unknown_keyword_shows_no_results_message(page):
    """Goal: verify empty search state displays friendly feedback.
    Precondition: none.
    Expected: 'There are no products found.' is displayed and zero product cards appear."""
    home = HomePage(page).open().search("zzz-no-such-tool")
    expect(home.no_results).to_contain_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


@pytest.mark.ui
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_sort_by_price_orders_products(page, order):
    """Goal: verify sorting grid by price in ascending and descending orders.
    Precondition: none.
    Expected: prices on the first page match sorted order."""
    home = HomePage(page).open().sort_by(order)
    expect(home.sorting_completed).to_be_visible()
    prices = home.prices()
    assert prices, "no product prices rendered"
    assert prices == sorted(prices, reverse=(order == "price,desc"))


# --- Group 2: Bộ lọc ---
@pytest.mark.ui
def test_filter_category_hammer_shows_matching_products(page):
    """Goal: verify category filter restricts product grid to matching category.
    Precondition: none.
    Expected: filter_completed is visible and every rendered product name contains 'hammer'."""
    home = HomePage(page).open().filter_by_category("Hammer")
    expect(home.filter_completed).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names, "no products rendered for Hammer category"
    assert all("hammer" in name.lower() for name in names), names


# --- Group 3: Chi tiết sản phẩm ---
@pytest.mark.ui
def test_product_detail_shows_name_and_price(page):
    """Goal: verify navigating to product details page displays correct name and unit price.
    Precondition: product 'Thor Hammer' is listed on homepage.
    Expected: product detail heading equals 'Thor Hammer' and unit price is positive."""
    product = HomePage(page).open().open_product("Thor Hammer")
    expect(product.name).to_have_text("Thor Hammer")
    assert product.price() > 0


# --- Group 4: Giỏ hàng ---
@pytest.mark.ui
def test_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: verify line price equals unit price multiplied by quantity and total matches sum of lines.
    Precondition: clean browser context with empty cart.
    Expected: line price equals unit price * 2 and cart total equals line price."""
    product = HomePage(page).open().open_product("Combination Pliers")
    expect(product.unit_price).to_be_visible()
    unit_price = product.price()
    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")
    cart = product.go_to_cart()
    expect(cart.total).to_be_visible()
    lines = cart.line_totals()
    assert len(lines) == 1
    assert lines[0] == pytest.approx(unit_price * 2)
    assert cart.total_value() == pytest.approx(sum(lines))


@pytest.mark.ui
def test_cart_continue_shopping_returns_to_home(page):
    """Goal: verify 'Continue Shopping' navigation action returns user to product catalog grid.
    Precondition: cart has at least one item.
    Expected: clicking continue shopping navigates back to catalog and products are visible."""
    cart = HomePage(page).open().open_product("Hammer").add_to_cart().go_to_cart()
    expect(cart.product_titles.first).to_contain_text("Hammer")
    cart.continue_shopping.click()
    home = HomePage(page)
    expect(home.product_names.first).to_be_visible()


# --- Group 5: Xác thực ---
@pytest.mark.ui
def test_login_empty_form_shows_required_errors(page):
    """Goal: verify submitting empty login form triggers required field validation errors.
    Precondition: none.
    Expected: 'Email is required' and 'Password is required' messages are shown."""
    login = LoginPage(page).open()
    login.submit_button.click()
    expect(login.email_error).to_contain_text("Email is required")
    expect(login.password_error).to_contain_text("Password is required")


# --- Group 6: Liên hệ, tài khoản ---
@pytest.mark.ui
def test_account_page_logged_in_shows_user_menu(logged_in_page):
    """Goal: verify reusing session auth_state via logged_in_page fixture grants account access.
    Precondition: session storage_state generated once by auth_state fixture.
    Expected: AccountPage opens directly with title 'My account' and user nav menu shows 'QA Bot'."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")
