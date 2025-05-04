from eth_utils import to_wei
import boa
from tests.conftest import SEND_VALUE

RANDOM_USER = boa.env.generate_address("non-owner")


def test_price_feed_id_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address

def test_starting_values(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether")
    assert coffee.OWNER() == account.address

def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts("You must spend more ETH!"):
        coffee.fund()

def test_fund_with_money(coffee, account):
    # Arrange
    boa.env.set_balance(account.address, SEND_VALUE)
    # Act
    coffee.fund(value=SEND_VALUE)
    # Assert
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE

def test_owner_can_withdraw(coffee_funded):
    with boa.env.prank(coffee_funded.OWNER()):
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.OWNER()) == SEND_VALUE
    assert boa.env.get_balance(coffee_funded.address) == 0


def test_non_owner_cannot_withdraw(coffee_funded):
    
    with boa.reverts("Not the contract owner!"):
        with boa.env.prank(RANDOM_USER):
            coffee_funded.withdraw()

def test_fund_multiple_users_and_owner_withdraw(coffee):
    # Arrange
    # Generate random users 
    random_users = [boa.env.generate_address(f"user_{i}") for i in range(10)]
    starting_owner_balance = boa.env.get_balance(coffee.OWNER())

    # Set balances for random users
    for user in random_users:
        boa.env.set_balance(user, SEND_VALUE)
        
    # Act
    # Fund the contract with multiple users
    for user in random_users:
        with boa.env.prank(user):
            coffee.fund(value=SEND_VALUE)


    # Owner withdraws
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()

    # Assert
    # Check that the contract balance is zero
    assert boa.env.get_balance(coffee.address) == 0
    # Check that the owner's balance is equal to the total amount funded
    total_funded = SEND_VALUE * len(random_users)

    assert boa.env.get_balance(coffee.OWNER()) == total_funded + starting_owner_balance

def test_get_rate(coffee):
    rate = coffee.get_eth_to_usd_rate(SEND_VALUE)
    assert rate > 0

def test_default_function(coffee):
    sender = boa.env.generate_address("sender")
    
    # Fund the sender address first
    boa.env.set_balance(sender, SEND_VALUE * 10)
    
    # Send ETH to the contract
    with boa.env.prank(sender):
        boa.env.raw_call(
            coffee.address,
            value=SEND_VALUE
        )
    # Verify the contract received the ETH
    assert boa.env.get_balance(coffee.address) == SEND_VALUE
    assert coffee.funder_to_amount_funded(sender) == SEND_VALUE