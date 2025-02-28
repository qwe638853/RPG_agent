# pragma version 0.4.0
"""
@title Character NFT (ERC-721)
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

# Define the CharacterStatus struct, including level and experience.
struct CharacterStatus:
    level: uint256         # Character level
    experience: uint256    # Experience points

# Mapping: token_id => CharacterStatus
character_status: public(HashMap[uint256, CharacterStatus])

# NFT counter
counter: public(uint256)
agent_admin: address

@deploy
def __init__(base_uri: String[80]):
    """
    Initialize the NFT contract and set the base Metadata URI.
    """
    ownable.__init__()
    erc721.__init__("Characters", "RPG", base_uri, "RPG Adventure", "1.0")
    self.counter = 0
    self.agent_admin = msg.sender

@external
def create_character(
    owner: address,
    metadata_uri: String[128],
):
    token_id: uint256 = self.counter

    # Mint the NFT and set the Metadata URI.
    erc721._safe_mint(owner, token_id, b"")
    erc721._set_token_uri(token_id, metadata_uri)

    # Set the initial character status: level 1, experience 0.
    self.character_status[token_id] = CharacterStatus(
        level=1,
        experience=0,
    )
    self.counter += 1


@external
def change_character(token_id:uint256 ,metadata_uri: String[128]):
    assert msg.sender == self.agent_admin, "Only admin can change character"
    erc721._set_token_uri(token_id, metadata_uri)


@external
def update_status(
    token_id: uint256,
    new_level: uint256,
    new_experience: uint256,
):
    """
    Update the status of the specified NFT (e.g., updating level and experience after leveling up).
    Only admin can update the status.
    """
    assert msg.sender == self.agent_admin, "Only admin can update status"
    status: CharacterStatus = self.character_status[token_id]
    status.level = new_level
    status.experience = new_experience

    self.character_status[token_id] = status

@internal
@pure
def _xp_required_for_level(level: uint256) -> uint256:
    """
    Calculate the XP required to level up to the specified level.
    e.g., level=2 => 20 XP, level=3 => 40 XP...
    Adjust this as needed.
    """
    if level == 1:
        return 0  # Level 1 requires no XP.
    return 10 * (2 ** (level - 1))

@external
def gain_experience(token_id: uint256, xp_gained: uint256):
    """
    Allow the character to gain XP: accumulate XP and, if sufficient, automatically level up.
    Only admin can call this.
    """
    assert msg.sender == self.agent_admin, "Only admin can modify XP"
    
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
    Query the status of the specified character (level, experience).
    """
    return self.character_status[token_id]

@external
def kill_character(token_id: uint256):
    """
    Burn the NFT and delete the associated character status.
    """
    assert msg.sender == self.agent_admin, "Only the owner can burn"
    erc721._burn(token_id)
    self.character_status[token_id] = empty(CharacterStatus)
