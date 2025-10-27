# Etherscan Portfolio Viewer

An Ethereum portfolio analysis app that uses the Etherscan API to provide comprehensive address analytics and portfolio tracking. The app features address validation, balance monitoring, transaction history, and token portfolio analysis.

## Features

### Address Validation & Information

- **Real-time Address Validation**: Validates Ethereum address format and connectivity
- **Balance Display**: Shows current ETH balance with account status
- **Activity Detection**: Identifies active vs. new/inactive accounts
- **Quick Links**: Direct links to Etherscan and ENS domains

### Portfolio Analytics

- **Transaction History**: Complete ETH transaction log with gas fee tracking
- **Token Transfers**: ERC-20 token transfer history with direction indicators
- **Token Balances**: Calculated current token holdings from transfer history
- **Visual Charts**: Interactive pie charts for token distribution analysis

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - Obtain a free API key from [Etherscan.io](https://etherscan.io/apis)
   - Add it to the `.env` file: `ETHERSCAN_API_KEY=your_key_here`

3. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Configure in OpenBB Workspace**:
   - Add the app via backend URL: `http://localhost:8000`
   - Start with the "Address Validator" widget to enter an Ethereum address
   - All other widgets will use the same address parameter

## How It Works

### Address Validator Widget

1. **Enter Address**: Input any Ethereum address (42 characters starting with 0x)
2. **Validation**: Widget validates format and fetches basic information:
   - 📍 **Prompt**: Instructions for entering a valid address
   - ✅ **Valid**: Shows ETH balance, account status, and useful links
   - ❌ **Invalid**: Format error with specific validation feedback
3. **Parameter Grouping**: Address automatically syncs to all other widgets

### Portfolio Widgets

1. **ETH Balance**: Displays current ETH balance as a metric widget
2. **Transaction History**: Tabular view of all ETH transactions with:
   - Date/time stamps
   - Transaction hashes (truncated)
   - From/To addresses (truncated)
   - ETH values and gas fees
   - Success/failure status with color coding
3. **Token Transfers**: ERC-20 token activity showing:
   - Token symbols and names
   - Transfer direction (IN/OUT) with color coding
   - Token amounts
   - Transaction details
4. **Token Balances**: Calculated holdings with pie chart visualization

## Example Ethereum Addresses

### 🏦 **High-Profile Addresses** (for testing with lots of activity)
| Address | Description | ETH Balance | Activity Level |
|---------|-------------|-------------|----------------|
| `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | Vitalik Buterin | ~3.75 ETH | Very High |
| `0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85` | ENS: Registrar | High | Very High |

### 👤 **Typical User Addresses** (better for demos)
| Address | Description | ETH Balance | Activity Level |
|---------|-------------|-------------|----------------|
| `0x8ba1f109551bD432803012645Hac136c9723499` | Regular DeFi User | ~0.1-0.5 ETH | Medium |
| `0x742637c89d44C6936b3C55A7E5a9D6F7ae80F1Ae` | NFT Collector | ~0.2-0.8 ETH | Medium |
| `0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67` | Token Trader | ~0.05-0.3 ETH | Medium |
| `0x6cc5f688a315f3dc28a7781717a9a798a59fda7b` | Casual User | ~0.01-0.1 ETH | Low |

### 🧪 **Test Addresses** (for edge cases)
| Address | Description | ETH Balance | Activity Level |
|---------|-------------|-------------|----------------|
| `0x1234567890123456789012345678901234567890` | New/Empty Wallet | 0 ETH | None |
| `0x0000000000000000000000000000000000000000` | Null Address | 0 ETH | None |
| `0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359` | Old Inactive Wallet | ~0.001 ETH | Very Low |

## Widget Configuration

The app includes 5 main widgets:

1. **Address Validator** (Markdown) - Full width header for address input
2. **ETH Balance** (Metric) - Compact balance display
3. **Transaction History** (Table) - Comprehensive transaction log
4. **Token Transfers** (Table) - ERC-20 transfer activity
5. **Token Balances** (Table/Chart) - Current holdings with pie chart

## Getting Your Etherscan API Key

1. Visit: https://etherscan.io/apis
2. Create a free account with Etherscan
3. Generate your API key
4. Add it to your `.env` file as `ETHERSCAN_API_KEY=your_key_here`

## API Endpoints Used

This app uses **Etherscan API V2** endpoints:

- **Balance**: `/v2/api?chainid=1&module=account&action=balance` - Get ETH balance
- **Transactions**: `/v2/api?chainid=1&module=account&action=txlist` - Get transaction history  
- **Token Transfers**: `/v2/api?chainid=1&module=account&action=tokentx` - Get ERC-20 transfers

All endpoints include `chainid=1` for Ethereum mainnet and return data formatted for OpenBB Workspace widgets.
