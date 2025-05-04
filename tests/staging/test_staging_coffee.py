import pytest
from moccasin.config import get_active_network
from script.deploy import deploy_coffee
from tests.conftest import SEND_VALUE
import boa
from eth_utils import to_wei

AMOUNT = to_wei(0.01, "ether")

@pytest.mark.staging
@pytest.mark.local
@pytest.mark.ignore_isolation
def test_can_fund_and_withdraw_live():
    active_network = get_active_network()
    price_feed = active_network.manifest_named("price_feed")
    coffee = deploy_coffee(price_feed)
    coffee.fund(value = AMOUNT)
    # amount_funded = coffee.address_to_amount(boa.env.eoa)
    # assert amount_funded == AMOUNT
    coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0