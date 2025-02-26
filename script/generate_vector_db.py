import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Set your OpenAI API Key
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables (adjust according to the actual path)
root_dir = Path(__file__).parent.parent

load_dotenv(root_dir / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load monster data
def load_monster_data(file_path="../vector_db/data/srd_5e_monsters.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def do_split_document(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=250 ,chunk_overlap=100)
    docs = text_splitter.split_documents(documents) 
    return docs

# Convert to LangChain Document format
def prepare_monster_documents(monsters):
    docs = []
    for monster in monsters:
        doc = Document(
             page_content=f"""
                {monster.get("name", "Unknown")} - {monster.get("meta", "No meta")}
                Armor Class: {monster.get("Armor Class", "N/A")}
                Hit Points: {monster.get("Hit Points", "N/A")}
                Speed: {monster.get("Speed", "N/A")}
                Stats: STR {monster.get("STR", "N/A")} DEX {monster.get("DEX", "N/A")} CON {monster.get("CON", "N/A")}
                INT {monster.get("INT", "N/A")} WIS {monster.get("WIS", "N/A")} CHA {monster.get("CHA", "N/A")}
                Saving Throws: {monster.get("Saving Throws", "None")}
                Skills: {monster.get("Skills", "None")}
                Challenge Rating: {monster.get("Challenge", "N/A")}
                Senses: {monster.get("Senses", "N/A")}
                Languages: {monster.get("Languages", "N/A")}
                Traits: {monster.get("Traits", "N/A")}
                Actions: {monster.get("Actions", "N/A")}
                Legendary Actions: {monster.get("Legendary Actions", "None")}
            """,
            metadata={
                "name": monster["name"],
                "CR": monster["Challenge"],
                "image_url": monster["img_url"],
            }
        )
        docs.append(doc)
    return docs

# Save vector database
def save_vector_db(docs, db_path="../vector_db"):
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(docs, embeddings)
    vector_db.save_local(db_path)
    print(f"✅ Vector database saved to `{db_path}`")

if __name__ == "__main__":
    print("🔄 Loading monster compendium...")
    monster_data = load_monster_data()
    print(f"📄 A total of {len(monster_data)} monsters")

    print("🛠 Converting monster data...")
    monster_docs = prepare_monster_documents(monster_data)

    print("🛠 Split monster docs...")
    splitted_docs = do_split_document(monster_docs)
    
    print("💾 Saving vector database...")
    save_vector_db(monster_docs)

    print("🎉 Vector database creation complete!")
