#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_etherscan_api():
    """Test the Etherscan API key."""
    api_key = os.getenv('ETHERSCAN_API_KEY')
    
    if not api_key:
        print("❌ No API key found in .env file")
        print("Please add: ETHERSCAN_API_KEY=your_key_here")
        return False
    
    print(f"🔑 Testing API key: {api_key[:10]}...")
    
    # Test with Vitalik's address
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    url = "https://api.etherscan.io/v2/api"
    
    params = {
        "chainid": "1",
        "module": "account",
        "action": "balance",
        "address": test_address,
        "tag": "latest",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 API response: {data}")
        
        if data.get("status") == "1":
            balance_wei = data.get("result", "0")
            balance_eth = float(balance_wei) / 10**18
            print(f"✅ API key is valid!")
            print(f"💰 Vitalik's ETH balance: {balance_eth:.4f} ETH")
            return True
        else:
            error_msg = data.get("message", "Unknown error")
            result = data.get("result", "No details")
            print(f"❌ API Error: {error_msg}")
            print(f"🔍 Details: {result}")
            
            if "Invalid API Key" in str(result):
                print("\n🚨 Your API key is invalid!")
                print("📝 Get a new key from: https://etherscan.io/apis")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Etherscan API Key")
    print("=" * 40)
    success = test_etherscan_api()
    
    if success:
        print("\n🎉 All good! Your app should work now.")
    else:
        print("\n🔧 Please fix the API key issue and try again.")