# ShopEasy E-Commerce FAQ Bot
Capstone Project | Agentic AI Course 2026

## Project Overview
A 24/7 intelligent customer support bot for ShopEasy, an e-commerce platform.
Built using LangGraph, ChromaDB, and Groq's LLaMA 3.3 model.
The bot answers customer queries from a 10-document knowledge base, remembers
conversation context across multiple turns, and uses a datetime tool for
live delivery date calculations.

## Files
- `agent.ipynb` — main notebook with all agent code, tests, and evaluation
- `capstone_streamlit.py` — Streamlit chat UI
- `requirements.txt` — all dependencies

## Setup Instructions

### Step 1 — Clone the repository
git clone https://github.com/Baidehi25/E-Commerce_FAQ_Bot.git</b>
cd E-Commerce_FAQ_Bot

### Step 2 — Create and activate a virtual environment
conda create -n EcommerceBot python=3.11
conda activate EcommerceBot

### Step 3 — Install dependencies
pip install -r requirements.txt

### Step 4 — Add your Groq API key
Get a free key from https://console.groq.com
Open `agent.ipynb` and `capstone_streamlit.py`, and replace `YOUR_GROQ_API_KEY`

### Step 5 — Run the notebook
Open `agent.ipynb` in VS Code, select the EcommerceBot kernel,
and run all cells from top to bottom using Shift+Enter.

### Step 6 — Launch the Streamlit UI
Ensure the environment is activated:
streamlit run capstone_streamlit.py --server.fileWatcherType none
