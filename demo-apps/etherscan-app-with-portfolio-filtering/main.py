import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Etherscan Portfolio Viewer",
    description="Ethereum address portfolio viewer using Etherscan API",
    version="0.0.1"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base URL for Etherscan API V2
ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"

def validate_eth_address(address: str) -> bool:
    """Validate Ethereum address format."""
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False

def wei_to_eth(wei_value: str) -> float:
    """Convert wei to ETH."""
    try:
        return float(wei_value) / 10**18
    except (ValueError, TypeError):
        return 0.0

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "Etherscan Portfolio Viewer"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Workspace"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/apps.json")
def get_apps():
    """Apps configuration file for the OpenBB Workspace"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "apps.json").open())
    )


@app.get("/address_info")
def address_info(address: str = "", api_key: str = ""):
    """Validate address and show basic information.
    
    Args:
        address (str): Ethereum address to validate
        api_key (str): Etherscan API key (optional, uses env if not provided)
    
    Returns:
        str: Markdown formatted address information
    """
    if not address:
        return """# 📍 Enter Ethereum Address

Please enter an Ethereum address above to view portfolio information.

**Valid address format:**
- Must start with `0x`
- Must be 42 characters long
- Must contain valid hexadecimal characters

**Example addresses:**
- **High Activity**: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` (Vitalik - 3.75 ETH)

---
*Enter an address to begin portfolio analysis.*"""
    
    if not validate_eth_address(address):
        return f"""# ❌ Invalid Address Format

The address you entered is not a valid Ethereum address.

**Address:** `{address}`

**Issues:**
{("- Address must start with 0x" if not address.startswith("0x") else "")}
{("- Address must be 42 characters long (current: " + str(len(address)) + ")" if len(address) != 42 else "")}
{("- Address must contain valid hexadecimal characters" if address.startswith("0x") and len(address) == 42 else "")}

---
*Please enter a valid Ethereum address.*"""
    
    # Get API key from parameter or environment
    if not api_key:
        api_key = os.getenv('ETHERSCAN_API_KEY')
    
    # For testing, we'll proceed without API key but warn about rate limits
    if not api_key:
        api_key = "YourApiKeyToken"  # Default for testing (with rate limits)
    
    try:
        # Fetch ETH balance
        params = {
            "chainid": "1",
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": api_key
        }
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1":
            balance_wei = data.get("result", "0")
            balance_eth = wei_to_eth(balance_wei)
            
            # Get transaction count
            tx_params = {
                "chainid": "1",
                "module": "account",
                "action": "txlist",
                "address": address,
                "page": "1",
                "offset": "1",
                "apikey": api_key
            }
            tx_response = requests.get(ETHERSCAN_API_URL, params=tx_params, timeout=10)
            tx_data = tx_response.json()
            
            # Note: This gives us limited info, but we can check if account has transactions
            has_transactions = tx_data.get("status") == "1" and len(tx_data.get("result", [])) > 0
            
            return f"""# ✅ Valid Ethereum Address

## Address
- `{address}`

## ETH Balance:
- {balance_eth:.6f} ETH

## Status:
- {"Active" if has_transactions else "New/Inactive"} Account

---
*Address validated successfully. View detailed data in the widgets below or [Etherscan](https://etherscan.io/address/{address}) or [ENS Names](https://app.ens.domains/address/{address})*"""
        
        else:
            error_msg = data.get("message", "Unknown error")
            result = data.get("result", "No additional info")
            
            # Check if it's an API key issue
            if "Invalid API Key" in error_msg or result == "Invalid API Key provided":
                return f"""# ❌ Invalid API Key

Your Etherscan API key is invalid.

**Steps to fix:**
1. Visit [Etherscan API Keys](https://etherscan.io/apis)
2. Sign up for a free account
3. Generate a new API key
4. Update your `.env` file: `ETHERSCAN_API_KEY=your_new_key`

**Current key (first 10 chars):** `{api_key[:10]}...`

---
*Please get a valid API key to continue.*"""
            
            return f"""# ⚠️ API Error

Failed to fetch address information.

**Error:** {error_msg}
**Details:** {result}

**Possible causes:**
- API key is invalid or rate limited
- Network connectivity issues  
- Etherscan API is temporarily unavailable

**Try:**
- Get a new API key from [Etherscan.io](https://etherscan.io/apis)
- Check your internet connection
- Wait and try again (rate limit)

---
*Please check your API key and try again.*"""
            
    except Exception as e:
        return f"""# ❌ Connection Error

Failed to connect to Etherscan API.

**Error:** {str(e)}

**Please check:**
- Internet connection
- API key validity
- Etherscan API status

---
*Unable to fetch address data.*"""


@app.get("/eth_balance")
def eth_balance(address: str = "", api_key: str = ""):
    """Get ETH balance for an address.
    
    Returns a single metric value.
    """
    if not address or not validate_eth_address(address):
        return {"value": "N/A", "label": "ETH Balance"}
    
    if not api_key:
        api_key = os.getenv('ETHERSCAN_API_KEY')
    
    if not api_key:
        return {"value": "No API Key", "label": "ETH Balance"}
    
    try:
        params = {
            "chainid": "1",
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": api_key
        }
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1":
            balance_wei = data.get("result", "0")
            balance_eth = wei_to_eth(balance_wei)
            return {"value": f"{balance_eth:.4f}", "label": "ETH Balance"}
        
        return {"value": "Error", "label": "ETH Balance"}
        
    except Exception:
        return {"value": "Error", "label": "ETH Balance"}

@app.get("/transactions")
def transactions(address: str = "", limit: int = 100, api_key: str = ""):
    """Get normal transactions for an address.
    
    Returns transaction data as a table.
    """
    if not address or not validate_eth_address(address):
        return []
    
    if not api_key:
        api_key = os.getenv('ETHERSCAN_API_KEY')
    
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        params = {
            "chainid": "1",
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": "0",
            "endblock": "99999999",
            "page": "1",
            "offset": str(limit),
            "sort": "desc",
            "apikey": api_key
        }
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1":
            transactions = data.get("result", [])
            
            # Process and format transactions
            formatted_txs = []
            for tx in transactions:
                timestamp = int(tx.get("timeStamp", 0))
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "N/A"
                
                formatted_txs.append({
                    "Date": date,
                    "Hash": tx.get("hash", "")[:10] + "...",
                    "From": tx.get("from", "")[:10] + "...",
                    "To": tx.get("to", "")[:10] + "...",
                    "Value (ETH)": f"{wei_to_eth(tx.get('value', '0')):.6f}",
                    "Gas Fee (ETH)": f"{wei_to_eth(str(int(tx.get('gasUsed', '0')) * int(tx.get('gasPrice', '0')))):.6f}",
                    "Status": "Success" if tx.get("isError") == "0" else "Failed",
                    "Block": tx.get("blockNumber", "")
                })
            
            return formatted_txs
        
        return []
        
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return []

@app.get("/token_transfers")
def token_transfers(address: str = "", limit: int = 100, api_key: str = ""):
    """Get ERC-20 token transfers for an address.
    
    Returns token transfer data as a table.
    """
    if not address or not validate_eth_address(address):
        return []
    
    if not api_key:
        api_key = os.getenv('ETHERSCAN_API_KEY')
    
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        params = {
            "chainid": "1",
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": "1",
            "offset": str(limit),
            "sort": "desc",
            "apikey": api_key
        }
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1":
            transfers = data.get("result", [])
            
            # Process and format token transfers
            formatted_transfers = []
            for transfer in transfers:
                timestamp = int(transfer.get("timeStamp", 0))
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "N/A"
                
                # Calculate token value with decimals
                token_decimal = int(transfer.get("tokenDecimal", "18"))
                value = float(transfer.get("value", "0")) / (10 ** token_decimal) if token_decimal > 0 else float(transfer.get("value", "0"))
                
                formatted_transfers.append({
                    "Date": date,
                    "Token": transfer.get("tokenSymbol", "Unknown"),
                    "Name": transfer.get("tokenName", "")[:20],
                    "From": transfer.get("from", "")[:10] + "...",
                    "To": transfer.get("to", "")[:10] + "...",
                    "Value": f"{value:.4f}",
                    "Direction": "IN" if transfer.get("to", "").lower() == address.lower() else "OUT",
                    "Hash": transfer.get("hash", "")[:10] + "..."
                })
            
            return formatted_transfers
        
        return []
        
    except Exception as e:
        print(f"Error fetching token transfers: {str(e)}")
        return []

@app.get("/token_balances")
def token_balances(address: str = "", api_key: str = ""):
    """Get current token balances by analyzing token transfers.
    
    Returns aggregated token balance data.
    """
    if not address or not validate_eth_address(address):
        return []
    
    if not api_key:
        api_key = os.getenv('ETHERSCAN_API_KEY')
    
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        # Get all token transfers to calculate balances
        params = {
            "chainid": "1",
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": "1",
            "offset": "10000",  # Get more transfers for accurate balance
            "sort": "asc",
            "apikey": api_key
        }
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "1":
            transfers = data.get("result", [])
            
            # Calculate balances by token
            token_balances = {}
            
            for transfer in transfers:
                token_symbol = transfer.get("tokenSymbol", "Unknown")
                token_name = transfer.get("tokenName", "")
                token_decimal = int(transfer.get("tokenDecimal", "18"))
                value = float(transfer.get("value", "0")) / (10 ** token_decimal) if token_decimal > 0 else float(transfer.get("value", "0"))
                
                if token_symbol not in token_balances:
                    token_balances[token_symbol] = {
                        "name": token_name,
                        "balance": 0,
                        "contract": transfer.get("contractAddress", "")
                    }
                
                # Add or subtract based on direction
                if transfer.get("to", "").lower() == address.lower():
                    token_balances[token_symbol]["balance"] += value
                else:
                    token_balances[token_symbol]["balance"] -= value
            
            # Format for output
            formatted_balances = []
            for symbol, info in token_balances.items():
                if info["balance"] > 0.0001:  # Filter out dust
                    formatted_balances.append({
                        "Token": symbol,
                        "Name": info["name"][:30],
                        "Balance": f"{info['balance']:.4f}",
                        "Contract": info["contract"][:10] + "..."
                    })
            
            # Sort by token symbol
            formatted_balances.sort(key=lambda x: x["Token"])
            
            return formatted_balances
        
        return []
        
    except Exception as e:
        print(f"Error calculating token balances: {str(e)}")
        return []