import boa
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def test_create_character(character_contract, default_account):
    """
    測試鑄造角色 NFT 並驗證基本資料：
      - NFT 的擁有者、Metadata URI
      - 角色狀態：等級 1、經驗 0、hit_points 根據 constitution 計算，
        並且能力值正確記錄
    """
    token_id = 1
    metadata_uri = "https://game.com/meta/character1.json"
    # 自定義角色能力值（例如：D&D 六大屬性）
    strength = 15
    dexterity = 12
    constitution = 14
    intelligence = 10
    wisdom = 8
    charisma = 13

    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        strength,
        dexterity,
        constitution,
        intelligence,
        wisdom,
        charisma,
        sender=default_account.address
    )

    # 驗證 NFT 擁有者
    assert character_contract.ownerOf(token_id) == default_account.address

  

    # 驗證 totalSupply 應增加
    assert character_contract.totalSupply() == 1

    # 取得角色狀態（返回 tuple）
    status = character_contract.character_status(token_id)
    # status = (level, experience, hit_points, attributes)
    assert status[0] == 1       # 等級
    assert status[1] == 0       # 經驗值
    # hit_points = 10 + ((constitution - 10) // 2)
    expected_hp = 10 + ((constitution - 10) // 2)
    assert status[2] == expected_hp

    # 驗證角色能力值
    attrs = status[3]  # 這是一個 tuple，依序為 (strength, dexterity, constitution, intelligence, wisdom, charisma)
    assert attrs[0] == strength
    assert attrs[1] == dexterity
    assert attrs[2] == constitution
    assert attrs[3] == intelligence
    assert attrs[4] == wisdom
    assert attrs[5] == charisma


def test_update_status(character_contract, default_account):
    """
    測試更新角色狀態（例如升級後更新等級、經驗值與血量）
    """
    token_id = 2
    metadata_uri = "https://game.com/meta/character2.json"
    # 鑄造角色，初始所有屬性均設為 10
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        10, 10, 10, 10, 10, 10,
        sender=default_account.address
    )
    # 更新狀態：假設角色升級為 5 級、經驗值 1000、血量 20
    new_level = 5
    new_experience = 1000
    new_hit_points = 20
    character_contract.update_status(token_id, new_level, new_experience, new_hit_points, sender=default_account.address)

    status = character_contract.character_status(token_id)
    # 用 tuple 索引取值
    assert status[0] == new_level
    assert status[1] == new_experience
    assert status[2] == new_hit_points


def test_update_attributes(character_contract, default_account):
    """
    測試更新角色能力值
    """
    token_id = 3
    metadata_uri = "https://game.com/meta/character3.json"
    # 先鑄造角色，初始所有屬性均設為 10
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        10, 10, 10, 10, 10, 10,
        sender=default_account.address
    )
    # 更新角色能力值
    new_strength = 18
    new_dexterity = 16
    new_constitution = 15
    new_intelligence = 12
    new_wisdom = 11
    new_charisma = 14
    character_contract.update_attributes(
        token_id,
        new_strength,
        new_dexterity,
        new_constitution,
        new_intelligence,
        new_wisdom,
        new_charisma,
        sender=default_account.address
    )
    status = character_contract.character_status(token_id)
    attrs = status[3]
    assert attrs[0] == new_strength
    assert attrs[1] == new_dexterity
    assert attrs[2] == new_constitution
    assert attrs[3] == new_intelligence
    assert attrs[4] == new_wisdom
    assert attrs[5] == new_charisma


def test_kill_character(character_contract, default_account):
    """
    測試銷毀角色 NFT 並驗證：
      - ownerOf(token_id) 會 revert，拋出 "erc721: invalid token ID"
      - 角色狀態被清空（各項數值為 0）
    """
    token_id = 4
    metadata_uri = "https://game.com/meta/character4.json"
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        10, 10, 10, 10, 10, 10,
        sender=default_account.address
    )
    character_contract.killCharacter(token_id, sender=default_account.address)
    
    # 檢查 ownerOf 呼叫應 revert，捕捉錯誤訊息
    with boa.reverts("erc721: invalid token ID"):
        character_contract.ownerOf(token_id)
    
    # 檢查角色狀態，應為 empty (tuple 中每個數值均為 0)
    status = character_contract.character_status(token_id)
    # 此處預期 empty(struct) 會返回 (0,0,0,(0,0,0,0,0,0))
    assert status[0] == 0
    assert status[1] == 0
    assert status[2] == 0
    attrs = status[3]
    for attr in attrs:
        assert attr == 0


def test_create_character_revert_duplicate(character_contract, default_account):
    """
    測試相同 token_id 重複鑄造時應 revert
    """
    token_id = 5
    metadata_uri = "https://game.com/meta/character5.json"
    # 第一次鑄造成功
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        12, 12, 12, 12, 12, 12,
        sender=default_account.address
    )
    # 第二次嘗試鑄造同一 token_id 應該 revert
    with boa.reverts():
        character_contract.create_character(
            token_id,
            default_account.address,
            metadata_uri,
            12, 12, 12, 12, 12, 12,
            sender=default_account.address
        )


def test_update_status_revert_not_owner(character_contract, default_account):
    """
    測試非擁有者調用 update_status 時應 revert
    """
    token_id = 6
    metadata_uri = "https://game.com/meta/character6.json"
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        10, 10, 10, 10, 10, 10,
        sender=default_account.address
    )
    attacker = boa.env.generate_address()
    with boa.reverts("Only owner can update status"):
        character_contract.update_status(token_id, 2, 500, 15, sender=attacker)


def test_update_attributes_revert_not_owner(character_contract, default_account):
    """
    測試非擁有者調用 update_attributes 時應 revert
    """
    token_id = 7
    metadata_uri = "https://game.com/meta/character7.json"
    character_contract.create_character(
        token_id,
        default_account.address,
        metadata_uri,
        10, 10, 10, 10, 10, 10,
        sender=default_account.address
    )
    attacker = boa.env.generate_address()
    with boa.reverts("Only owner can update attributes"):
        character_contract.update_attributes(
            token_id,
            15, 15, 15, 15, 15, 15,
            sender=attacker
        )
