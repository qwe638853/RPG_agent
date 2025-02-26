from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from .ipfs_connection import update_ipfs_metadata
from .contract_interaction import gain_xp
import re
import json
import uuid

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)

store = {}



def parse_gpt_response(gpt_text: str) -> dict:
    result = {"xp_gained": 0, "hp_change": 0}
    
    # 優先嘗試抓取 JSON 區塊（假設 JSON 在回應末尾）
    json_match = re.search(r'\{.*?\}', gpt_text.strip().replace("\n", " "), re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            result["xp_gained"] = int(data.get("xp_gained", 0))
            result["hp_change"] = int(data.get("hp_change", 0))
            return result
        except Exception as e:
            # 如果解析失敗則繼續使用正則表達式備援
            pass
    return result

def analyze_and_process_response(response):
    """在 LLM 回應後解析內容，擷取 XP 與 HP 變化，並決定是否要修改回應。"""
    
    changes = parse_gpt_response(response)
    
    xp_gained = changes["xp_gained"]
    hp_change = changes["hp_change"]

    system_update = []

    if hp_change != 0:
        character_status["attributes"][2]["value"] = character_status["attributes"][2]["value"] + hp_change
    if xp_gained != 0:
        character_status["attributes"][1]["value"] = character_status["attributes"][1]["value"] + xp_gained

    try:
        if hp_change!=0 or xp_gained!=0:    
            update_ipfs_metadata(character_tokenURI,character_status)
            if xp_gained!=0: 
                gain_xp(character_tokenId,xp_gained)
    except Exception as e:
        print("Update error:",e)
                
            
    return response


def create_conversation_chain():
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        system_prompt = (f"""
            You are the AI Dungeon Master, guiding the player through an immersive and dynamic dungeon adventure. Your role is to blend captivating storytelling with structured, turn-based combat mechanics to create a seamless Dungeons & Dragons (D&D) experience.

            ## Core Principles:
            1. Adaptive Storytelling – Expand the narrative dynamically with creative twists and engaging descriptions.
            2. Balanced Combat – Implement structured, round-based combat when triggered, ensuring fairness and excitement.
            3. Automated Dice Rolls – Perform and narrate dice rolls (e.g., d20 for attack/defense, d6/d8 for damage).
            4. Combat Feedback – Provide enemy health hints (e.g., "The goblin looks weary") rather than exact numbers.
            5. Concise yet Immersive Responses – Keep descriptions rich but avoid redundancy from previous turns.


            [Character Data]:
            - Name: {character_status.get("name", "Unknown")}
            - Level: {character_status.get("attributes")[0].get("value", "N/A")}
            - Experience: {character_status.get("attributes")[1].get("value", "N/A")}
            - Hit Points: {character_status.get("attributes")[2].get("value", "N/A")}
            - Attributes:
            - Strength: {character_status.get("attributes")[3].get("value", "N/A")}
            - Dexterity: {character_status.get("attributes")[4].get("value", "N/A")}
            - Constitution: {character_status.get("attributes")[5].get("value", "N/A")}
            - Intelligence: {character_status.get("attributes")[6].get("value", "N/A")}
            - Wisdom: {character_status.get("attributes")[7].get("value", "N/A")}
            - Charisma: {character_status.get("attributes")[8].get("value", "N/A")}

            [Gameplay Rules]
            1. Story Progression
            - Always move the narrative forward with vivid descriptions.
            - Offer three or more meaningful choices per turn.
            - Adapt to unexpected player actions with creative improvisation.

            2. Combat Mechanics
            - Attack/Defense: Use a d20 roll.
            - Damage: Use d6 or d8 rolls (based on weapons and abilities).
            - Auto-roll for NPCs while allowing the player to make key decisions.
            - Describe combat impact clearly (e.g., “Your sword barely grazes the orc” or “The skeleton crumbles under your mighty blow”).

            3. Status Updates
            - Continuously track and update player **HP** and enemy conditions.
            - Provide **non-numerical** enemy health feedback (e.g., "The dragon stumbles, struggling to stay airborne").
            - Update status dynamically while keeping the battle engaging.

            4. XP & HP Tracking
            - Monitor all XP gains and HP changes, even if values remain at 0.
            - If HP changes or XP is gained, append a JSON-formatted summary at the end of the response:{{"xp_gained": <xp_value>, "hp_change": <hp_value>}}
            
            Final Enhancements:
                Maintain a balance between structured mechanics and fluid roleplaying elements.
                Keep player agency at the core, ensuring their actions meaningfully shape the world.
                Always provide immersive, cinematic descriptions, but avoid redundancy for a seamless experience.
        """)
        initial_scene = """
            You stands before the entrance of an ancient dungeon. The grand door is slightly ajar, and thick mist seeps through the cracks, as if whispering dangerous warnings.
            Beside the door, there is a broken stone tablet with the inscription: "Entrants must purchase their chance to survive with Soul."
            You possesses wears meager equipment, and is surrounded by the low murmur of a cold wind, as if no one is willing to accompany you inside.
        """
        
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
            store[session_id].add_message(SystemMessage(content=system_prompt))
            store[session_id].add_ai_message(initial_scene)
        
        
        return store[session_id]
    
    
    llm=ChatOpenAI(temperature=0.3)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """
            You are the AI Dungeon Master. When combat is triggered, please resolve the encounter in 2–3 rounds and automatically roll the dice for every action.

            **Rules:**
            1. **Simplified Combat:** When combat begins, aim to conclude the battle within 2–3 rounds (each round corresponding to one message). Avoid lengthy, drawn-out encounters.
            2. **Automated Dice Rolls:** Perform all necessary dice rolls automatically (e.g., using a d20 for attack and defense, and a d6 or d8 for damage) and include the results in your narration. The player does not need to roll any dice.
            3. **Concise Narration:** In each round, provide a brief description of the action, including the dice roll outcomes and the resulting changes (e.g., damage dealt). Keep the narrative short and impactful.
            4. **Status Summary:** At the end of each round, append a JSON-formatted summary indicating any changes in XP and HP. For example:
            {{
                "xp_gained": <XP_value>,
                "hp_change": <HP_value>
            }}
            5. **Narrative Continuity:** While the descriptions should remain immersive, they must also quickly advance the combat narrative to a swift conclusion.
            6. **Final Outcome:** By the end of the 2–3 rounds, the combat should be decisively resolved—whether the enemy is defeated or the player suffers significant damage—with clear results provided via the JSON summary.
            7. **Interesting Events:** Outside of combat encounters, incorporate engaging and unexpected narrative events. These events could be puzzles, mysterious encounters, or roleplaying challenges that add depth and excitement to the overall adventure.
            
            Remember, the goal is to quickly and automatically resolve combat while maintaining a coherent narrative.
            """
        ),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    routed_chain = RunnableWithMessageHistory(
        runnable=(
            {"input": RunnablePassthrough()}  # 傳遞輸入
            | chat_prompt  # 使用語意相似度選擇 Prompt
            | llm  # 呼叫 LLM
            | StrOutputParser()  # 解析輸出
            | RunnableLambda(analyze_and_process_response)
        ), # ✅ 讓 AI 存取對話歷史 # ✅ 讓每個 session 有獨立記憶
        get_session_history = get_session_history,
    )
        
    # 🎯 修正 7：確保記憶體與對話系統綁定
    return routed_chain

    
def start_conversation(character:dict,tokenURI:str,token_id:int):
    global character_status, character_tokenURI, character_tokenId
    character_status = character
    character_tokenURI = tokenURI
    character_tokenId = token_id
    print(character_status)
    conversation = create_conversation_chain()
    
    print("\n🔥 You have arrived at the mysterious dungeon entrance 🔥")
    print("(Type 'exit' or 'quit' to leave the conversation。T)\n")
    
    while True:
        user_input = input("Player: ")
        if user_input.lower() in {"exit", "quit"}:
            print("You have chosen to leave the dungeon... Game over.")
            break
        response = conversation.invoke({"input": user_input},{"configurable": {"session_id": "default_session"}})
        print("Dungeon Master:", response)


