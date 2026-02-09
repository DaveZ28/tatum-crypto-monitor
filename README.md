# Tatum Ethereum Crypto Monitor

A simple Python CLI tool that monitors activity of an Ethereum address using the **Tatum Platform**.

---

## Features

The tool:
- Fetches **ETH balance** via the Tatum Ethereum RPC Gateway  
- Retrieves **recent transaction history** via Tatum Data API (v4)  
- Summarizes:
  - number of incoming vs outgoing transfers  
  - native ETH inflow and outflow  
  - number of token-related transfers  
  - timestamp of the last activity  
- Displays a readable table of recent transactions in the terminal

---

## Architecture

The project is split into three main modules:

- `tatum_client.py`  
  Handles all communication with Tatum APIs (RPC + Data API).

- `analyze.py`  
  Processes raw transaction data and produces meaningful summaries.

- `monitor.py`  
  CLI entry point that ties everything together and prints results.

## Setup & Run

### 1) Clone
git clone https://github.com/DaveZ28/tatum-crypto-monitor.git

cd tatum-crypto-monitor

### 2) Install dependencies
python -m pip install -r requirements.txt

### 3) Configure API key
Copy `.env.example` to `.env` and set your Tatum API key:

TATUM_API_KEY=your_key_here

### 4) Run
python src/monitor.py --address 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --limit 20
