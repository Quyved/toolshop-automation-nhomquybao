Feature: Shopping cart pricing
  As a shopper
  I want to search for a product and add it to my cart with a chosen quantity
  So that I can see accurate line prices and cart totals before checkout

  Background:
    Given I am on the home page

  Scenario Outline: Cart calculates line price and total for a searched product
    When I search for "<keyword>"
    And I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    And I view the shopping cart
    Then the cart shows "<product>" with quantity <quantity>
    And the line price equals the unit price times <quantity>
    And the cart total equals the sum of all line prices

    Examples:
      | keyword | product            | quantity |
      | pliers  | Combination Pliers | 1        |
      | hammer  | Claw Hammer        | 3        |
      | hammer  | Hammer             | 2        |
