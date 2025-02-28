# RPG_agent

RPG Agent is an innovative interactive role-playing game (RPG) inspired by Dungeons & Dragons, incorporating NFT-based characters and on-chain progression to create a truly immersive experience. Players can develop their characters, embark on procedurally generated adventures, and engage in dynamic storytelling powered by AI.

## Tech Stack

- **Vyper & Snekmate** – A Pythonic smart contract language (Vyper) along with the Snekmate library, used for creating NFT-based D&D characters and managing on-chain character progression efficiently.
- **LLM** – Utilizes OpenAI for AI-driven storytelling, interactive dialogue, and procedural content generation.
- **IPFS** – Uses Pinata as a decentralized storage service for pinning and managing character metadata
- **Python** – The core language powering the CLI-based game interface and backend logic.
- **Blochain network** – Uses Anvil as a local blockchain simulator for testing and development, providing a realistic blockchain environment.

## Setting up environment

1. Install uv
```
pip install uv
```
2. Set up a virtual environment

```
uv venv
```

3. active the virtual environment
```bash
source .venv/bin/activate
```

4. install the Python dependencies

```
uv pip install requirements.txt
```
5. install the moccasin dependencies
```
uv run moccasin install
```

6. set up `.env`<br>
Set up `.env` file and fill in the values based on the provided `example.env` file

## Running test

```
mox test --network anvil 
```

## Deploying the Token Deployer Contract
```
mox run deploy --network anvil
```

## Rinning game
```
mox run game --network anvil
```

## How to play 

### Create your character 
When you create your character, you'll be prompted to enter your character's name and provide a brief background description. The AI will generate an image based on your description, bringing your unique character to life as an NFT.
### Start your travel 
Once your character is created, you can begin your adventure. As you travel, you'll have the freedom to choose your actions and shape your story. And if you're ever unsure of what to do next, the RPG Agent will guide you by suggesting narrative options to keep the adventure moving forward.

## Future Prospects & Roadmap

This version serves as a conceptual demo, showcasing the core mechanics and possibilities of RPG Agent. There is significant room for future advancements and enhancements, including:
- NFT Swap & Marketplace – Implement an on-chain marketplace where players can trade, buy, and sell NFT-based characters, items, and collectibles.

- Web-Based Interface – Expand from a CLI-based experience to a fully interactive web-based UI, making it more user-friendly.

- In-Game Economy – Detail plans for an internal economy where players can earn, trade, or spend tokens, possibly integrating with DeFi protocols.

- Achievements & Leaderboards – Outline a system for tracking player milestones and showcasing top adventurers.


