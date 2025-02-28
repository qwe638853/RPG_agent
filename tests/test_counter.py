import boa
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
base_uri = "https://ipfs.io/ipfs/"

def test_create_character(character_contract, default_account):
    """
    Test creating a character NFT and verify the basic data:
      - NFT owner and Metadata URI
      - Character status: level 1, experience 0
    """
    metadata_uri = "bafkreiglnb5fntnlr33cxg4f4d5p4fjfrwn4gehcpiyv5x7hllbvegm7ku"  # simulate CID
    
    # Call create_character: the contract automatically uses a counter as token_id, with the first token_id being 0
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)

    token_id = 0
    # Verify the NFT owner
    assert character_contract.ownerOf(token_id) == default_account.address

    # Verify totalSupply is 1
    assert character_contract.totalSupply() == 1

    # Verify tokenURI
    assert character_contract.tokenURI(token_id) == base_uri + metadata_uri

    # Verify character status: level 1, experience 0
    status = character_contract.query_character(token_id)
    assert status[0] == 1   # level
    assert status[1] == 0   # experience


def test_update_status(character_contract, default_account):
    """
    Test updating the character status:
      - Only admin is allowed to update status
      - After updating, the character status should reflect the new level and experience
    """
    metadata_uri = "https://game.com/meta/character2.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0

    # Admin (default_account) updates the character status
    new_level = 5
    new_experience = 1000
    character_contract.update_status(token_id, new_level, new_experience, sender=default_account.address)

    status = character_contract.query_character(token_id)
    assert status[0] == new_level   
    assert status[1] == new_experience


def test_gain_experience(character_contract, default_account):
    """
    Test the character gaining experience:
      - Only admin is allowed to call gain_experience
      - When the accumulated experience exceeds the level-up threshold, the character should automatically level up and the remaining experience is correctly calculated
    """
    metadata_uri = "https://game.com/meta/character3.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0

    # Assume the initial status is level 1, experience 0; according to _xp_required_for_level, 20 XP is needed to reach level 2
    xp_to_gain = 25  # 25 XP should level up the character to level 2, with 5 XP remaining
    character_contract.gain_experience(token_id, xp_to_gain, sender=default_account.address)

    status = character_contract.query_character(token_id)
    assert status[0] == 2   # level
    assert status[1] == 5   # experience


def test_kill_character(character_contract, default_account):
    """
    Test burning (killing) a character NFT:
      - kill_character can only be called by admin
      - After burning, ownerOf(token_id) should revert, and the character status should be cleared (level and experience set to 0)
    """
    metadata_uri = "https://game.com/meta/character4.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0

    character_contract.kill_character(token_id, sender=default_account.address)
    
    with boa.reverts("erc721: invalid token ID"):
        character_contract.ownerOf(token_id)
    
    status = character_contract.query_character(token_id)
    assert status[0] == 0   # level
    assert status[1] == 0   # experience


def test_create_character_multiple(character_contract, default_account):
    """
    Test creating multiple character NFTs:
      - Each creation should generate a new token_id, and totalSupply should increase accordingly
    """
    metadata_uri1 = "https://game.com/meta/character5.json"
    metadata_uri2 = "https://game.com/meta/character6.json"
    character_contract.create_character(default_account.address, metadata_uri1, sender=default_account.address)
    character_contract.create_character(default_account.address, metadata_uri2, sender=default_account.address)

    # There should be two NFTs, with token_ids 0 and 1 respectively
    assert character_contract.totalSupply() == 2
    assert character_contract.tokenURI(0) == base_uri + metadata_uri1
    assert character_contract.tokenURI(1) == base_uri + metadata_uri2


def test_update_status_revert_not_admin(character_contract, default_account):
    """
    Test that calling update_status from a non-admin account should revert.
    """
    metadata_uri = "https://game.com/meta/character7.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0
    attacker = boa.env.generate_address()

    with boa.reverts("Only admin can update status"):
        character_contract.update_status(token_id, 2, 500, sender=attacker)


def test_gain_experience_revert_not_admin(character_contract, default_account):
    """
    Test that calling gain_experience from a non-admin account should revert.
    """
    metadata_uri = "https://game.com/meta/character8.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0
    attacker = boa.env.generate_address()

    with boa.reverts("Only admin can modify XP"):
        character_contract.gain_experience(token_id, 100, sender=attacker)


def test_kill_character_revert_not_admin(character_contract, default_account):
    """
    Test that calling kill_character from a non-admin account should revert.
    """
    metadata_uri = "https://game.com/meta/character9.json"
    character_contract.create_character(default_account.address, metadata_uri, sender=default_account.address)
    token_id = 0
    attacker = boa.env.generate_address()

    with boa.reverts("Only the owner can burn"):
        character_contract.kill_character(token_id, sender=attacker)
        
def test_change_character(character_contract, default_account):
    """
    Test that an admin (default_account) can successfully change the token's metadata URI.
    """
    # Mint a new character NFT
    original_metadata_uri = "https://game.com/meta/character_change.json"
    character_contract.create_character(
        default_account.address, 
        original_metadata_uri, 
        sender=default_account.address
    )
    token_id = 0

    # The new metadata URI we want to set
    new_metadata_uri = "bafkreichangemetadata"

    # Change the token's metadata URI
    character_contract.change_character(
        token_id, 
        new_metadata_uri, 
        sender=default_account.address
    )

    # Assuming the contract prepends "https://ipfs.io/ipfs/" to the CID
    base_uri = "https://ipfs.io/ipfs/"
    # Verify the tokenURI has been updated
    assert character_contract.tokenURI(token_id) == base_uri + new_metadata_uri


def test_change_character_revert_not_admin(character_contract, default_account):
    """
    Test that calling change_character from a non-admin account reverts with "Only admin can change character".
    """
    # Mint a new character NFT
    original_metadata_uri = "https://game.com/meta/character_change2.json"
    character_contract.create_character(
        default_account.address, 
        original_metadata_uri, 
        sender=default_account.address
    )
    token_id = 0

    # The new metadata URI
    new_metadata_uri = "bafkreichangemetadata2"

    # Generate a random attacker address
    attacker = boa.env.generate_address()

    # Attempting to change the URI as a non-admin should revert
    with boa.reverts("Only admin can change character"):
        character_contract.change_character(
            token_id, 
            new_metadata_uri, 
            sender=attacker
        )

