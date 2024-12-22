import os
from web3 import Web3
from eth_account import Account
import secrets
import json
from typing import Dict, Optional, List
import click
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ['INFURA_API_KEY', 'ETHERSCAN_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print("Error: Missing required environment variables:")
    print("\n".join(missing_vars))
    print("\nPlease create a .env file with the following variables:")
    print("INFURA_API_KEY=your_infura_key_here")
    print("ETHERSCAN_API_KEY=your_etherscan_key_here")
    sys.exit(1)

class CryptoWallet:
    def __init__(self, network: str = "sepolia"):
        """Initialize wallet with network connection"""
        # Network configurations
        self.networks = {
            "sepolia": {
                "url": f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
                "explorer": "https://api-sepolia.etherscan.io/api",
                "explorer_key": os.getenv('ETHERSCAN_API_KEY'),
                "faucet": "https://sepoliafaucet.com/",
            },
            "goerli": {
                "url": f"https://goerli.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
                "explorer": "https://api-goerli.etherscan.io/api",
                "explorer_key": os.getenv('ETHERSCAN_API_KEY'),
                "faucet": "https://goerlifaucet.com/",
            }
        }
        
        self.network = network
        self.web3 = Web3(Web3.HTTPProvider(self.networks[network]["url"]))
        self.accounts = {}
        
        # Create wallets directory if it doesn't exist
        os.makedirs('wallets', exist_ok=True)
        self._load_existing_wallets()

    def _load_existing_wallets(self):
        """Load existing wallet files from the wallets directory"""
        if not os.path.exists('wallets'):
            return
            
        for filename in os.listdir('wallets'):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join('wallets', filename), 'r') as f:
                        wallet_data = json.load(f)
                        self.accounts[wallet_data['address']] = wallet_data
                except Exception as e:
                    print(f"Error loading wallet {filename}: {str(e)}")

    def create_wallet(self) -> Dict[str, str]:
        """Generate a new wallet with private and public keys"""
        private_key = secrets.token_hex(32)
        account = Account.from_key(private_key)
        
        wallet_data = {
            'address': account.address,
            'private_key': private_key,
            'public_key': self.web3.keccak(text=account.address).hex()
        }
        
        wallet_path = os.path.join('wallets', f"{account.address}.json")
        with open(wallet_path, 'w') as f:
            json.dump(wallet_data, f, indent=4)
        
        self.accounts[account.address] = wallet_data
        return wallet_data

    def request_airdrop(self, address: str) -> Dict[str, str]:
        """Request testnet tokens from faucet"""
        if not self.web3.is_address(address):
            raise ValueError("Invalid address")
            
        faucet_url = self.networks[self.network]["faucet"]
        return {
            "status": "success",
            "message": f"Please visit {faucet_url} to request tokens for address: {address}",
            "network": self.network
    }

    def send_transaction(self, from_address: str, to_address: str, amount: float) -> str:
        """Send ETH from one address to another"""
        if from_address not in self.accounts:
            raise ValueError("Sender address not found in wallet")
        
        # Get the private key
        private_key = self.accounts[from_address]['private_key']
        
        # Prepare transaction
        nonce = self.web3.eth.get_transaction_count(from_address)
        gas_price = self.web3.eth.gas_price
        
        # Convert amount to Wei
        value_in_wei = self.web3.to_wei(amount, 'ether')
        
        # Build transaction dictionary
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': value_in_wei,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': self.web3.eth.chain_id
        }
        
        # Sign and send transaction
        signed_txn = self.web3.eth.account.sign_transaction(transaction, "0x" + private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # Wait for transaction receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return self.web3.to_hex(tx_hash)

    def get_transaction_history(self, address: str) -> List[Dict]:
        """Get transaction history for an address using block explorer"""
        if not self.web3.is_address(address):
            raise ValueError("Invalid address")
            
        api_url = self.networks[self.network]["explorer"]
        api_key = self.networks[self.network]["explorer_key"]
        
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "1":
                return self._format_transactions(data["result"])
        return []

    def _format_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Format transaction data for better readability"""
        formatted = []
        for tx in transactions:
            formatted.append({
                "hash": tx["hash"],
                "from": tx["from"],
                "to": tx["to"],
                "value": self.web3.from_wei(int(tx["value"]), "ether"),
                "gas_used": tx["gasUsed"],
                "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S'),
                "status": "Success" if tx["txreceipt_status"] == "1" else "Failed"
            })
        return formatted

    def analyze_transaction(self, tx_hash: str) -> Dict:
        """Get detailed transaction analysis"""
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "transaction": {
                    "hash": tx_hash,
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": self.web3.from_wei(tx["value"], "ether"),
                    "gas_price": self.web3.from_wei(tx["gasPrice"], "gwei"),
                    "gas_limit": tx["gas"],
                    "nonce": tx["nonce"]
                },
                "receipt": {
                    "status": "Success" if receipt["status"] == 1 else "Failed",
                    "gas_used": receipt["gasUsed"],
                    "block_number": receipt["blockNumber"],
                    "block_hash": self.web3.to_hex(receipt["blockHash"]),
                    "logs": len(receipt["logs"])
                }
            }
        except Exception as e:
            raise ValueError(f"Error analyzing transaction: {str(e)}")

@click.group()
def cli():
    """Cryptocurrency Wallet CLI"""
    pass

@cli.command()
def create():
    """Create a new wallet"""
    try:
        wallet = CryptoWallet()
        new_wallet = wallet.create_wallet()
        click.echo("\nCreated new wallet:")
        click.echo(f"Address: {new_wallet['address']}")
        click.echo(f"Private key: {new_wallet['private_key']}")
        click.echo(f"Public key: {new_wallet['public_key']}")
    except Exception as e:
        click.echo(f"Error creating wallet: {str(e)}")

@cli.command()
@click.argument('address')
def airdrop(address):
    """Request testnet tokens for an address"""
    try:
        wallet = CryptoWallet()
        result = wallet.request_airdrop(address)
        click.echo(f"\nAirdrop request: {result['message']}")
    except Exception as e:
        click.echo(f"Error requesting airdrop: {str(e)}")

@cli.command()
@click.argument('from_address')
@click.argument('to_address')
@click.argument('amount', type=float)
def send(from_address, to_address, amount):
    """Send ETH to another address"""
    try:
        wallet = CryptoWallet()
        tx_hash = wallet.send_transaction(from_address, to_address, amount)
        click.echo(f"\nTransaction sent successfully!")
        click.echo(f"Transaction hash: {tx_hash}")
    except Exception as e:
        click.echo(f"Error sending transaction: {str(e)}")

@cli.command()
@click.argument('address')
def history(address):
    """Get transaction history for an address"""
    try:
        wallet = CryptoWallet()
        transactions = wallet.get_transaction_history(address)
        if not transactions:
            click.echo("No transactions found")
            return
            
        click.echo("\nTransaction History:")
        for tx in transactions:
            click.echo("-" * 80)
            click.echo(f"Hash:      {tx['hash']}")
            click.echo(f"From:      {tx['from']}")
            click.echo(f"To:        {tx['to']}")
            click.echo(f"Value:     {tx['value']} ETH")
            click.echo(f"Status:    {tx['status']}")
            click.echo(f"Timestamp: {tx['timestamp']}")
    except Exception as e:
        click.echo(f"Error fetching history: {str(e)}")

@cli.command()
@click.argument('tx_hash')
def analyze(tx_hash):
    """Analyze a specific transaction"""
    try:
        wallet = CryptoWallet()
        analysis = wallet.analyze_transaction(tx_hash)
        
        click.echo("\nTransaction Analysis:")
        click.echo("\nTransaction Details:")
        for key, value in analysis['transaction'].items():
            click.echo(f"{key.replace('_', ' ').title()}: {value}")
            
        click.echo("\nReceipt Details:")
        for key, value in analysis['receipt'].items():
            click.echo(f"{key.replace('_', ' ').title()}: {value}")
    except Exception as e:
        click.echo(f"Error analyzing transaction: {str(e)}")

def main():
    cli(prog_name='wallet.py')

if __name__ == '__main__':
    main()