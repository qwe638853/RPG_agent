import pytest
import moccasin
from src import Character  # Import the contract module from src/Character.vy
from moccasin.boa_tools import VyperContract
from moccasin.config import get_config
from moccasin.moccasin_account import MoccasinAccount

@pytest.fixture
def character_contract() -> VyperContract:
    """
    Deploys the contract and returns the contract object.
    Pass in the base_uri parameter (e.g., https://game.com/meta/)
    """
    return Character.deploy("https://ipfs.io/ipfs/")

@pytest.fixture
def default_account() -> MoccasinAccount:
    """
    Retrieves the default account from the test network.
    """
    return moccasin.config.get_active_network().get_default_account()
