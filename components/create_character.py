import random
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path


root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


def generate_character() -> dict:
    """
    讓玩家輸入角色描述，並隨機生成角色能力值
    """
    name = input("請輸入角色名字： ")
    description = input("請輸入你的角色背景描述： ")
    """
    response = client.images.generate(
        model="dall-e-2",
        prompt=f"A D&D fantasy character: {description}",
        n=1,
        size="512x512"
    )
    image_url = response.data[0].url
    """
    
    image_url = ""
    attributes = {
        "strength": random.randint(5, 20),
        "dexterity": random.randint(5, 20),
        "constitution": random.randint(5, 20),
        "intelligence": random.randint(5, 20),
        "wisdom": random.randint(5, 20),
        "charisma": random.randint(5, 20)
    }

    character_data = {
        "name": name,
        "image": image_url,
        "description": description,
        "attributes": attributes
    }
    return character_data
