# RPG_agent

RPG Agent is an innovative interactive role-playing game (RPG) inspired by Dungeons & Dragons, incorporating NFT-based characters and on-chain progression to create a truly immersive experience. Players can develop their characters, embark on procedurally generated adventures, and engage in dynamic storytelling powered by AI.

## Tech Stack

- **Vyper & Snekmate** – A Pythonic smart contract language (Vyper) along with the Snekmate library, used for creating NFT-based D&D characters and managing on-chain character progression efficiently.
- **LLM** – Utilizes OpenAI for AI-driven storytelling, interactive dialogue, and procedural content generation.
- **IPFS** – Uses Pinata as a decentralized storage service for pinning and managing character metadata
- **Python** – The core language powering the CLI-based game interface and backend logic.
- **Blochain network** – Uses Anvil as a local blockchain simulator for testing and development, providing a realistic blockchain environment.

## Setting up environment

1.Install uv
```
pip install uv
```
2.Set up a virtual environment

```
uv venv
```

3.active the virtual environment
```bash
source .venv/bin/activate
```

4.install the Python dependencies

```
uv pip install requirements.txt
```
5.install the moccasin dependencies
```
uv run moccasin install
```

6.set up `.env`
Set up `.env` file and fill in the values based on the provided `example.env` file

## Running test

```
mox run test --network anvil 
```

## Deploying the Token Deployer Contract
```
mox run deploy --network anvil
```

## Rinning game
```
mox run game --network anvil
```

## Future Prospects & Roadmap

This version serves as a conceptual demo, showcasing the core mechanics and possibilities of RPG Agent. There is significant room for future advancements and enhancements, including:
- NFT Swap & Marketplace – Implement an on-chain marketplace where players can trade, buy, and sell NFT-based characters, items, and collectibles.

- Web-Based Interface – Expand from a CLI-based experience to a fully interactive web-based UI, making it more user-friendly.

_For documentation, please run `mox --help` or visit [the Moccasin documentation](https://cyfrin.github.io/moccasin)_
