# CLI Wallet Implementation

## Overview
A simple CLI  wallet implementation in Python for cryptocurrency transactions.

## Tech Stack
- Python 3.x
- Click
- web3
- eth_account

## Project Structure
```
Wallets/
├── wallet.py          # Main wallet functionality
├── .env              # Environment variables
└── wallets/          # Generated wallet storage
    └── *.json        # Individual wallet files
```
## Dependencies
```bash
pip install web3 python-dotenv eth_account
```

## Quick Start
```bash
clone repository 
cd wallet 
```

## Environment Variables

Create a .env file with the following

```python
INFURA_URL=your_infura_endpoint
PRIVATE_KEY=your_private_key
```

## Features

- Basic key pair generation
- Transaction signing
- Airdrop transaction
- Analyze transactions on the blockchain(Arbitrum Sepolia)

## Usage

Generate wallet

```python
python wallet.py create
```

Send Transaction

```python
python wallet.py send <from_address> <to_address> <amount>
```

Airdrop Tokens

```python
python wallet.py airdrop <to_address>
```

Analyze Transactions

```python
Python wallet.py analyze <tx_hash>
```

![alt text](<Screenshot (230).png>)

- wallet info displayed will be terminated
- value balance is 0 transaction could not be completed
- only transactions on arbitrum sepolia network can be analyzed.

