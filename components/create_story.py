from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from .ipfs_connection import update_ipfs_metadata,delete_ipfs
from .contract_interaction import gain_xp,change_character,query_level,burn_character
import re
import json
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)

store = {}

# Get summary from history message
def save_adventure_summary(session_id: str):
    global character_status, character_tokenURI, character_tokenId
    if session_id in store:
        # Get conversation history messages list, skipping the first message (typically the system prompt)
        history = store[session_id].messages  
        history_summary = "\n".join([msg.content for msg in history[1:]])

        prompt = (
            """
            Summarize the following conversation into a very short and concise adventure log, 
            only describing the actions taken and key events, and DO NOT include any details 
            about experience points or health values:\n\n"
            """+ history_summary
        )
        llm = ChatOpenAI(temperature=0.3)
        summary = llm.invoke(prompt) # LLM generate summary
        character_status["adventure_log"] = summary.content
        try:
            cid = update_ipfs_metadata(character_status)
            character_tokenURI = cid
            change_character(character_tokenId,character_tokenURI)  
            
            print("Adventure summary uploaded to IPFS!")
        except Exception as e:
            print("Failed to update adventure summary:", e)
    else:
        print("No conversation history found for session:", session_id)
        
       
# Extract the XP&HP change values from response
def parse_gpt_response(gpt_text: str) -> dict:
    result = {"xp_gained": 0, "hp_change": 0}
    
    json_match = re.search(r'\{.*?\}', gpt_text.strip().replace("\n", " "), re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            result["xp_gained"] = int(data.get("xp_gained", 0))
            result["hp_change"] = int(data.get("hp_change", 0))
            return result
        except Exception as e:
            print("parse error:",e)
    return result

# Process GPT Response and Update State  
def analyze_and_process_response(response):
    
    global character_status, character_tokenURI, character_tokenId
    changes = parse_gpt_response(response)
    
    xp_gained = changes["xp_gained"]
    hp_change = changes["hp_change"]

    if hp_change != 0:
        character_status["attributes"][2]["value"] = character_status["attributes"][2]["value"] + hp_change
        if character_status["attributes"][2]["value"]<=0:   # character die
            burn_character(character_tokenId)
            
            

    cleaned_response = re.sub(r'\{.*?\}$', '', response, flags=re.DOTALL).strip()

    try:
        if hp_change!=0 or xp_gained!=0:    
            if xp_gained!=0: 
                gain_xp(character_tokenId,xp_gained)  # update xp on chain
                character_level,character_experience = query_level(character_tokenId) # query level&experience on chain
                character_status["attributes"][0]["value"] = character_level    
                character_status["attributes"][1]["value"] = character_experience   
            
            
            cid = update_ipfs_metadata(character_status)  # update ipfs 
            delete_ipfs(character_tokenURI.rstrip("/").split("/")[-1]) # delete previous character
            character_tokenURI = cid
            change_character(character_tokenId,character_tokenURI)  # change character's metadata
        
            
                
    except Exception as e:
        print("Update error:",e)
                
            
    return cleaned_response

# Create Conversation Chain with LangChain
def create_conversation_chain():
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        merged_system_prompt = f"""
            You are the AI Dungeon Master, guiding a player through a dynamic Dungeons & Dragons style adventure.
            
            # Instructions:
            - Provide immersive storytelling and vivid battle descriptions.
            - Do NOT include any speaker labels such as "Dungeon Master:" or "AI Dungeon Master:" in your final response.
            - Your output should be a plain narrative without extra prefixes or role names.
        
            # Core Directives
            1. Storytelling:
            - Be immersive and adaptive. Expand the narrative with creativity.
            - Each turn, provide the player with 3 or more distinct choices or actions.
            - The player’s decisions shape the world—be ready to improvise.

            2. Simplified Combat:
            - When combat starts, resolve it within 2–3 rounds total (each round is one AI response).
            - For each round:
                a. Player Attack: Perform a d20 roll. If hit, roll damage (d6 or d8).
                b. Enemy Attack: If enemy still alive, it also does a d20 roll and deals damage on hit.
            - Provide short but vivid descriptions; avoid lengthy drawn-out battles.

            3. XP & HP Tracking:
            - Always track "xp_gained" and "hp_change".
            - At the end of each response, append a JSON summary: {{ "xp_gained": <xp_value>, "hp_change": <hp_value> }}
            - If no change, use zero.

            4. Enemy Health Feedback:
            - Never show exact HP. Use flavor text (e.g. "The goblin staggers...").

            5. Character Data (for reference):
            Name: {character_status.get("name", "Unknown")}
            Level: {character_status["attributes"][0]["value"]}
            XP: {character_status["attributes"][1]["value"]}
            HP: {character_status["attributes"][2]["value"]}
            Strength: {character_status["attributes"][3]["value"]}
            Dexterity: {character_status["attributes"][4]["value"]}
            Constitution: {character_status["attributes"][5]["value"]}
            Intelligence: {character_status["attributes"][6]["value"]}
            Wisdom: {character_status["attributes"][7]["value"]}
            Charisma: {character_status["attributes"][8]["value"]}

            # Initial Scene
            "You stand before the entrance of an ancient dungeon. The massive stone door is slightly ajar, with a dense mist creeping out. 
            A shattered tablet beside the door reads: 'Only those who dare shall claim the treasures within.' 
            Your meager gear rattles slightly, and a chill wind howls behind you, as if no one dares follow you inside." """
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
            store[session_id].add_message(SystemMessage(content=merged_system_prompt))

        
        return store[session_id]
    
    
    llm=ChatOpenAI(temperature=0.3)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    # Build the conversation chain with message history and processing logic.
    routed_chain = RunnableWithMessageHistory(
        runnable=(
            {"input": RunnablePassthrough()}  
            | chat_prompt  
            | llm  #
            | StrOutputParser()  
            | RunnableLambda(analyze_and_process_response)
        ), 
        get_session_history = get_session_history,
    )
        

    return routed_chain


# Main Conversation Entry Point 
def start_conversation(character:dict,tokenURI:str,token_id:int):
    global character_status, character_tokenURI, character_tokenId
    character_status = character
    character_tokenURI = tokenURI
    character_tokenId = token_id

    conversation = create_conversation_chain()
    session_id = "default_session"
    print("\n🔥 You have arrived at the mysterious dungeon entrance 🔥")
    print("(Type 'exit' or 'quit' to leave and save the conversation。)\n")
    
    while True:
        user_input = input("Player: ")
        if user_input.lower() in {"exit", "quit"}:
            print("You have chosen to leave the dungeon... Game over.")
            # Before exiting, save the adventure summary and upload it to IPFS.
            save_adventure_summary(session_id)
            break
        if character_status["attributes"][2]["value"] <= 0:
            print("Your character has perished. Game Over.")
            break
        response = conversation.invoke({"input": user_input},{"configurable": {"session_id": session_id}})
        print("Dungeon Master:", response)


