import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables (adjust according to actual path)
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

PINATA_JWT = os.getenv("PINATA_JWT_TOKEN")

def upload_ipfs(character: dict):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    character_metadata = {
        "name": f"{character["name"]}",
        "description": f"{character["description"]}",
        "image": f"{character["image"]}",
        "attributes": [
            {"trait_type": "level", "value": 1},
            {"trait_type": "experience", "value": 0},
            {"trait_type": "hit point", "value": 10 + ((character["attributes"]["constitution"]-5)//2)},
            {"trait_type": "strength", "value": character["attributes"]["strength"]},
            {"trait_type": "dexterity", "value": character["attributes"]["dexterity"]},
            {"trait_type": "constitution", "value": character["attributes"]["constitution"]},
            {"trait_type": "intelligence", "value": character["attributes"]["intelligence"]},
            {"trait_type": "wisdom", "value": character["attributes"]["wisdom"]},
            {"trait_type": "charisma", "value": character["attributes"]["charisma"]}
        ]
    }
    payload = {
        "pinataOptions": {"cidVersion": 1},
        "pinataMetadata": {"name": "pinnie.json"},
        "pinataContent": character_metadata
    }
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response)
    
    Cid = response.json().get("IpfsHash")
    return Cid

def get_ipfs_json(CID: str):
    try:
        response = requests.get(CID)
        json_data = response.json()
        return json_data
    except Exception as e:
        print(f"connection ipfs failed: {e}")
        
def update_ipfs_metadata(cid: str, keyvalues: dict = None):
    """
    使用 PUT 請求更新 Pinata 上已經存在的 IPFS 資源（metadata）。
    - cid: Pinata 回傳的 IPFS Hash (IpfsPinHash)
    - name: 更新後的名稱 (string)
    - keyvalues: 你想要更新或新增的自定義鍵值對 (dict)
    文件參考: https://docs.pinata.cloud/pinning-services/pinata-api#operation/UpdateMetadata
    """
    url = "https://api.pinata.cloud/pinning/hashMetadata"
    
    # 根據 Pinata 文件，至少要傳 ipfsPinHash
    payload = {"ipfsPinHash": cid}

    # 如果有指定 keyvalues，就放進 payload
    if keyvalues is not None:
        payload["keyvalues"] = keyvalues
    
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Successfully updated metadata on Pinata!")
    else:
        print("Failed to update metadata. Status code:", response.status_code)
        print("Response:", response.text)
    
    # 回傳 API 回應的 JSON
    return response.json()

    
    