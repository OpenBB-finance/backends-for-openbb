# Etherscan Portfolio Viewer

An Ethereum portfolio analysis app that uses the Etherscan API to provide comprehensive address analytics and portfolio tracking. The app features address validation, balance monitoring, transaction history, and token portfolio analysis.

Note that the first widget is utilized to validate the address and then it's grouped to the ones below (although hidden in their parameters).

<img width="600" alt="CleanShot 2025-10-27 at 20 33 41@2x" src="https://github.com/user-attachments/assets/43f16078-1f0d-49b1-a2c8-420e689a850a" />

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key (Choose one method)**:
   
   **Method A - Environment Variable:**
   - Obtain a free API key from [Etherscan.io](https://etherscan.io/apis)
   - Add it to the `.env` file: `ETHERSCAN_API_KEY=your_key_here`
   
   **Method B - Authentication Header:**
   - Get your API key from [Etherscan.io](https://etherscan.io/apis)
   - Configure OpenBB Workspace with custom header: `X-ETHERSCAN-API-KEY: your_key_here`

3. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Configure in OpenBB Workspace**:
   - Add the app via backend URL: `http://localhost:8000`
   - Start with the "Address Validator" widget to enter an Ethereum address
   - All other widgets will use the same address parameter
  
<img width="600" alt="CleanShot 2025-10-27 at 20 33 28@2x" src="https://github.com/user-attachments/assets/aca108e9-62d1-4038-95a9-4b0f60f5a9db" />

## How It Works

### Address Validator Widget

1. **Enter Address**: Input any Ethereum address (42 characters starting with 0x)
2. **Validation**: Widget validates format and fetches basic information:
   - 📍 **Prompt**: Instructions for entering a valid address
   - ✅ **Valid**: Shows ETH balance, account status, and useful links
   - ❌ **Invalid**: Format error with specific validation feedback
3. **Parameter Grouping**: Address automatically syncs to all other widgets

### Authentication

The app supports two authentication methods:

1. **Environment Variable**: Set `ETHERSCAN_API_KEY` in your `.env` file
2. **Custom Header**: Send API key via `X-ETHERSCAN-API-KEY` header

The app will check for the header first, then fall back to the environment variable. This allows flexible deployment where OpenBB Workspace can manage the API key via headers.
