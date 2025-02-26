# pragma version 0.4.0
"""
@title D&D 角色 NFT（ERC-721）
@notice 這是一個以龍與地下城系統為靈感的 NFT 智能合約，
        支援 ERC-721 標準、EIP-4494 和 EIP-4906，
        並只在鍊上保留角色進度（等級、經驗與血量），
        角色的詳細能力值（力量、敏捷等）放在 IPFS metadata 中。
"""

from snekmate.tokens import erc721
from snekmate.auth import ownable

initializes: ownable
initializes: erc721[ownable := ownable]

exports:(
    erc721.ownerOf,
    erc721.tokenURI,
    erc721.totalSupply,
    erc721.burn,
    erc721.tokenOfOwnerByIndex,
    erc721.balanceOf
)

# 定義角色狀態結構，包含等級、經驗值、血量
struct CharacterStatus:
    level: uint256         # 角色等級
    experience: uint256    # 經驗值

# 映射：token_id => CharacterStatus
character_status: public(HashMap[uint256, CharacterStatus])

# NFT 計數器
counter: public(uint256)

@deploy
def __init__(base_uri: String[80]):
    """
    初始化 NFT 合約，並設置基礎 Metadata URI
    """
    ownable.__init__()
    erc721.__init__("D&D Characters", "DND", base_uri, "D&D EIP712", "1.0")
    self.counter = 0

@external
def create_character(
    owner: address,
    metadata_uri: String[128],
):
    """
    鑄造新的角色 NFT。
    角色能力值改為放在 IPFS Metadata 中（由 metadata_uri 指向）。
    
    參數：
    - owner: NFT 擁有者地址
    - metadata_uri: 該 NFT 對應的 IPFS（或其他）Metadata URI

    """
    token_id: uint256 = self.counter

    # 鑄造 NFT 並設定 Metadata
    erc721._safe_mint(owner, token_id, b"")
    erc721._set_token_uri(token_id, metadata_uri)

    # 設定角色初始狀態：等級 1，經驗 0，血量 = initial_hp
    self.character_status[token_id] = CharacterStatus(
        level=1,
        experience=0,
    )

    self.counter += 1

@external
def update_status(
    token_id: uint256,
    new_level: uint256,
    new_experience: uint256,
):
    """
    更新指定 NFT 的角色狀態（例如升級後更新等級、經驗值與血量）。
    只有 NFT 擁有者才能更新其狀態。
    """
    assert erc721._owner_of(token_id) == msg.sender, "Only owner can update status"
    status: CharacterStatus = self.character_status[token_id]
    status.level = new_level
    status.experience = new_experience

    self.character_status[token_id] = status

@internal
@pure
def _xp_required_for_level(level: uint256) -> uint256:
    """
    計算升級到指定等級所需的 XP。
    e.g.  level=2 => 20 XP, level=3 => 40 XP...
    可根據需求自行調整。
    """
    if level == 1:
        return 0  # level 1 不需要 XP
    return 10 * (2 ** (level - 1))

@external
def gain_experience(token_id: uint256, xp_gained: uint256):
    """
    角色獲得 XP：疊加後若足夠升級，則自動升級。
    只有 NFT 擁有者能呼叫。
    """
    assert erc721._owner_of(token_id) == msg.sender, "Only owner can modify XP"
    
    status: CharacterStatus = self.character_status[token_id]
    status.experience += xp_gained

    
    next_level_threshold: uint256 = self._xp_required_for_level(status.level + 1)
    if status.experience >= next_level_threshold and next_level_threshold > 0:
        status.level += 1
        status.experience -= next_level_threshold
    
    self.character_status[token_id] = status

@external
@view
def query_character(token_id: uint256) -> CharacterStatus:
    """
    查詢指定角色狀態（等級、經驗、血量）。
    """
    return self.character_status[token_id]

@external
def kill_character(token_id: uint256):
    """
    銷毀 NFT，並刪除該 NFT 對應的角色狀態。
    """
    assert erc721._owner_of(token_id) == msg.sender, "Only the owner can burn"
    erc721._burn(token_id)
    self.character_status[token_id] = empty(CharacterStatus)
