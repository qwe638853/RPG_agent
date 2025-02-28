import os
from pathlib import Path
from dotenv import load_dotenv
from moccasin.config import get_config
from moccasin.named_contract import NamedContract
from moccasin.moccasin_account import MoccasinAccount
from .ipfs_connection import get_ipfs_json

# Load environment variables (adjust according to actual path)
root_dir = Path(__file__).parent
load_dotenv(root_dir / ".env")

ABI = [
  {
    "inputs": [
      {
        "name": "base_uri",
        "type": "string"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "address"
      },
      {
        "name": "metadata_uri",
        "type": "string"
      }
    ],
    "name": "create_character",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      },
      {
        "name": "metadata_uri",
        "type": "string"
      }
    ],
    "name": "change_character",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      },
      {
        "name": "new_level",
        "type": "uint256"
      },
      {
        "name": "new_experience",
        "type": "uint256"
      }
    ],
    "name": "update_status",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      },
      {
        "name": "xp_gained",
        "type": "uint256"
      }
    ],
    "name": "gain_experience",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "name": "query_character",
    "outputs": [
      {
        "components": [
          {
            "name": "level",
            "type": "uint256"
          },
          {
            "name": "experience",
            "type": "uint256"
          }
        ],
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "name": "kill_character",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "name": "ownerOf",
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "name": "tokenURI",
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "name": "burn",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "address"
      },
      {
        "name": "index",
        "type": "uint256"
      }
    ],
    "name": "tokenOfOwnerByIndex",
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

# Obtain the deployed smart contract via Moccasin
def get_contract():

    network = get_config().get_active_network()
    default_wallet = network.get_default_account()
    contract: NamedContract = network.manifest_named_contract(
        contract_name="Character",
        abi=ABI,
        address="0x7C4b6ad0828dAE64c1678D624f94FAc3C2912db2"
    )
    return contract, default_wallet

# Query all character of address on chain 
def query_characters():
    contract, default_wallet = get_contract()
    try:
        balance = contract.balanceOf(default_wallet)
        print(f"Wallet {default_wallet} owns {balance} tokens.\n")
        json_datas = []
        token_URIs = []
        token_IDs = []
        for i in range(balance):
            # get tokenID
            token_id = contract.tokenOfOwnerByIndex(default_wallet, i)
            print("tokenId:", token_id, "\n")
            token_URI = contract.tokenURI(token_id)
            json_data = get_ipfs_json(token_URI)
            json_datas.append(json_data)
            token_URIs.append(token_URI)
            token_IDs.append(token_id)
        return json_datas, token_URIs, token_IDs
    except Exception as e:
        print(f"Query character failed: {e}\n")

# Query character level
def query_level(token_id: int):
    contract, default_wallet = get_contract()
    try:
        character_status = contract.query_character(token_id)
        return character_status
    except Exception as e:
        print(f"Query character failed: {e}\n")
        return None

# Gain xp on chain
def gain_xp(token_id: int, gained_xp: int):
    contract, default_wallet = get_contract()
    try:
        print(f"Attempting to add {gained_xp} XP to token {token_id}...\n")
        contract.gain_experience(token_id, gained_xp)
        print(f"Token {token_id} has successfully gained {gained_xp} XP.\n")
    except Exception as e:
        print(f"Failed to update XP for token {token_id}: {e}\n")

# Update character metadata
def change_character(token_id: int, token_URI: str):
    contract, default_wallet = get_contract()
    try:
        contract.change_character(token_id, token_URI)
    except Exception as e:
        print(f"Failed to change token for {token_id}: {e}\n")

# Kill character
def burn_character(token_id: int):
    contract, default_wallet = get_contract()
    try:
        contract.kill_character(token_id)
    except Exception as e:
        print(f"Failed to burn character for token: {e}\n")

# Mint character
def mint_character(character: dict, tokenURI: str):
    contract, default_wallet = get_contract()
    try:
        print("mint_character_tokenURI:", tokenURI, "\n")
        txn = contract.create_character(
            default_wallet,  # Wallet address
            tokenURI
        )
        print(f"Character minted successfully! Transaction hash: {txn}\n")
    except Exception as e:
        print(f"Transaction failed: {e}\n")
