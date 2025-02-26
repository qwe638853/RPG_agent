import pytest
import moccasin
from src import Character  # 從 src/Character.vy 導入合約模組
from moccasin.boa_tools import VyperContract
from moccasin.config import get_config
from moccasin.moccasin_account import MoccasinAccount

@pytest.fixture
def character_contract() -> VyperContract:
    """
    部署合約並返回合約對象，
    傳入 base_uri 參數（例如：https://game.com/meta/）
    """
    return Character.deploy("https://game.com/meta/")

@pytest.fixture
def default_account() -> MoccasinAccount:
    """
    獲取測試網的默認帳戶
    """
    return moccasin.config.get_active_network().get_default_account()
