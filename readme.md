# Ethereum Wallet Generator
A simple Python-based Ethereum wallet generator and transaction tool.

## Features
- Generate new Ethereum wallets
- Save wallet details securely
- Check wallet balances
- Send ETH transactions

## Tech Stack
- Python 3.x
- web3.py
- eth_account
- json
- os

## Project Structure

```
Wallets/
├── wallet.py        # Main wallet functionality
├── .env             # Environment variables
└── wallets/         # Generated wallet storage
    └── *.json       # Individual wallet files
```

## Installation

```bash
# Install required packages
pip install web3 python-dotenv eth_account

Usage

Generate New Wallet

