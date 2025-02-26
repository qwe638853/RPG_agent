from src import Character  # Ensure that `Character` is a Vyper contract
from moccasin.boa_tools import VyperContract
from moccasin.config import get_active_network

# Set the `base_uri` (the base URI for NFT Metadata, can use IPFS or a server)
BASE_URI = "https://ipfs.io/ipfs/"

def deploy_character() -> VyperContract:
    """
    Deploy the Character ERC-721 smart contract
    """
    character_contract = Character.deploy(BASE_URI)
    return character_contract

def deploy() -> VyperContract:
    """
    Deploy and verify the smart contract
    """
    character_contract = deploy_character()
    result = get_active_network().moccasin_verify(character_contract)
    result.wait_for_verification()
    return character_contract

def moccasin_main() -> VyperContract:
    return deploy_character()
