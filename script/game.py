from components.create_character import generate_character
from components.contract_interaction import mint_character,query_characters,burn_character
from components.create_story import start_conversation
from components.ipfs_connection import upload_ipfs




def character_select_info(character:dict):
    print("Load character...")
    print("Name       :", character.get("name"))
    print("Description:", character.get("description"))
    print("Level:", character.get("attributes")[0].get("value"))
    
def main():
    print("\n🔥 Welcome to RPG agent game 🔥")
    while True:
        print("\n=== Main Menu ===")
        print("1. Create character")
        print("2. Start game")
        print("3. Query character")
        print("4. Burn")
        print("0. Exit")
        
        choice = input("Select an option: ").strip()
        
        json_datas,token_URIs,token_IDs = query_characters()
        if choice == "1":
            # Start a new game: generate a character, upload metadata, mint NFT, then start conversation.
            try:
                
                character = generate_character()
                tokenURI = upload_ipfs(character)
                mint_character(character, tokenURI)
                
            except Exception as e:
                print("Error Creating character:", e)
                
        elif choice == "2":
            # Query character: ask for token ID and display character info.
            try:
                if len(json_datas)==0:
                    character = generate_character()
                    tokenURI = upload_ipfs(character)
                    mint_character(character, tokenURI)
                elif len(json_datas)==1:
                    character_select_info(json_datas[0])
                    start_conversation(json_datas[0],token_URIs[0],token_IDs[0])
                else:
                    for index, data in enumerate(json_datas):
                        print(f"{index + 1}: {data.get('name', 'Unknown')} - Experience: {data.get("attributes")[1].get("value")} - Level: {data.get("attributes")[0].get("value")}")
                    try:
                        choice_index = int(input("Select a character by number: ")) - 1
                        if 0 <= choice_index < len(json_datas):
                            character_select_info(json_datas[choice_index])
                            start_conversation(json_datas[choice_index],token_URIs[choice_index],token_IDs[choice_index])
                        else:
                            print("Invalid selection. Returning to main menu.")
                    except ValueError:
                        print("Invalid input. Returning to main menu.")
                    

                
            except Exception as e:
                print("Error starting game:", e)
                
        elif choice == "3":
            # Query character: ask for token ID and display character info.
            try:
                if len(json_datas) == 0:
                    print("No characters found. Please create a character first.")
                else:
                    for json_data in json_datas:
                        print("===================================")
                        print(f"Name        : {json_data.get('name', 'N/A')}")
                        print(f"Description : {json_data.get('description', 'N/A')}")
                        print(f"Image URL   : {json_data.get('image', 'N/A')}")
                        print("\nAttributes:")
                        for attr in json_data.get("attributes", []):
                            print(f"  {attr.get('trait_type', 'N/A')}: {attr.get('value', 'N/A')}")
            except Exception as e:
                print("Error querying character:", e)
                
        elif choice == "4":
            # Burn character: ask for token ID and burn the character NFT.
            try:
                for index, data in enumerate(json_datas):
                        print(f"{index + 1}: {data.get('name', 'Unknown')} - Experience: {data.get("attributes")[1].get("value")} - Level: {data.get("attributes")[0].get("value")}")
                burn_index = int(input("Enter number to burn character: ").strip())
                
                burn_character(token_IDs[burn_index])
                print("Character burned successsfully.")
            except Exception as e:
                print("Error burning character:", e)
                
        elif choice == "0":
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
    

   
    
# Moccasin entry point
def moccasin_main():
    return main()
