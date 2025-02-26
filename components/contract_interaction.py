import os
from pathlib import Path
from dotenv import load_dotenv
from moccasin.config import get_config
from moccasin.named_contract import NamedContract
from .ipfs_connection import get_ipfs_json

# Load environment variables (adjust according to actual path)
root_dir = Path(__file__).parent
load_dotenv(root_dir / ".env")

ABI = [
  {
    "type": "constructor",
    "stateMutability": "nonpayable",
    "inputs": [
      {
        "name": "base_uri",
        "type": "string"
      }
    ]
  },
  {
    "type": "function",
    "name": "create_character",
    "stateMutability": "nonpayable",
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
    "outputs": []
  },
  {
    "type": "function",
    "name": "update_status",
    "stateMutability": "nonpayable",
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
    "outputs": []
  },
  {
    "type": "function",
    "name": "gain_experience",
    "stateMutability": "nonpayable",
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
    "outputs": []
  },
  {
    "type": "function",
    "name": "query_character",
    "stateMutability": "view",
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "tuple",
        "components": [
          {
            "name": "level",
            "type": "uint256"
          },
          {
            "name": "experience",
            "type": "uint256"
          }
        ]
      }
    ]
  },
  {
    "type": "function",
    "name": "kill_character",
    "stateMutability": "nonpayable",
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "outputs": []
  },
  {
    "type": "function",
    "name": "ownerOf",
    "stateMutability": "view",
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ]
  },
  {
    "type": "function",
    "name": "tokenURI",
    "stateMutability": "view",
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ]
  },
  {
    "type": "function",
    "name": "totalSupply",
    "stateMutability": "view",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ]
  },
  {
    "type": "function",
    "name": "burn",
    "stateMutability": "nonpayable",
    "inputs": [
      {
        "name": "token_id",
        "type": "uint256"
      }
    ],
    "outputs": []
  },
  {
    "type": "function",
    "name": "tokenOfOwnerByIndex",
    "stateMutability": "view",
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
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ]
  },
  {
    "type": "function",
    "name": "balanceOf",
    "stateMutability": "view",
    "inputs": [
      {
        "name": "owner",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ]
  }
  
  
]



def get_contract():
    """
    Obtain the deployed smart contract via Moccasin
    """
    network = get_config().get_active_network()
    default_wallet = network.get_default_account()
    contract: NamedContract = network.manifest_named_contract(
        contract_name="Character",
        abi=ABI,
        address="0x1471D40Ba5564d548255CE4C538a2c8Fc7DEa927"
    )
    print("Contract information:", contract)
    return contract, default_wallet

def query_character():
    contract, default_wallet = get_contract()
    try:
        balance = contract.balanceOf(default_wallet)
        print(f"Wallet {default_wallet} owns {balance} tokens.")
        json_datas = []
        token_URIs = []
        token_IDs = []
        for i in range(balance):
            # get tokenID
            token_id = contract.tokenOfOwnerByIndex(default_wallet,i)
            print("tokenId:",token_id)
            character_status = contract.query_character(token_id)   #return (level,exp)
            token_URI = contract.tokenURI(token_id)
            json_data = get_ipfs_json(token_URI)
            json_datas.append(json_data)
            token_URIs.append(token_URI)
            token_IDs.append(token_id)
        return json_datas,token_URIs,token_IDs
        
    except Exception as e:
        print(f"Query character failed: {e}")
            
            
def gain_xp(token_id:int ,gained_xp:int ):
    contract, default_wallet = get_contract()
    try:
        print(f"Attempting to add {gained_xp} XP to token {token_id}...")
        contract.gain_experience(token_id, gained_xp)
        print(f"Token {token_id} has successfully gained {gained_xp} XP.")
    except Exception as e:
        print(f"Failed to update XP for token {token_id}: {e}")
        
        
        
def mint_character(character: dict,tokenURI: str):
    """
    Invoke the smart contract `create_character()` to mint a character NFT
    """
    contract, default_wallet = get_contract()

    try:
        print("mint_character_tokenURI:",tokenURI)
        txn = contract.create_character(
            default_wallet,                      # Wallet address
            tokenURI
        )
        print(f"Character minted successfully! Transaction hash: {txn}")
    except Exception as e:
        print(f"Transaction failed: {e}")
