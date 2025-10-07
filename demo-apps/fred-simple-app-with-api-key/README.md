# Simple App with API key

A simple FRED Series app that relies on user's API keys. There's a tab that is called API keys that holds a markdown widget with an API key parameter that is grouped to the FRED Series widget.

## Features

### API Key Mmnagement

- **Separate API Key Tab**: Configure your FRED API key in a dedicated tab
- **Real-time Validation**: Instant feedback on API key validity with detailed status messages
- **Parameter Grouping**: API key automatically syncs between widgets
- **Hidden Integration**: Main widget uses API key seamlessly without exposing it to users

### FRED Series visualization

- **Multi-Series Support**: Fetch multiple FRED series simultaneously (e.g., `RPI,PCE,UNRATE`)
- **Interactive Charts**: Built-in line chart visualization with toggle between table and chart views
- **Time Series Optimization**: Proper date handling and time-based charting
- **Data Quality**: Robust handling of missing data, NaN values, and edge cases

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Configure in OpenBB Workspace**:
   - Add the app via backend URL: `http://localhost:8000`
   - Navigate to "API Key" tab to set up your FRED API key
   - Use "Overview" tab for data visualization

## How It Works

### API Key Tab

1. **Enter API Key**: Input your FRED API key in the text field
2. **Validation**: Widget tests the key against FRED's API and shows status:
   - ⚠️ **Key Required**: Instructions for getting an API key
   - ✅ **Valid Key**: Confirmation with access details  
   - ❌ **Invalid Key**: Error message with troubleshooting tips
3. **Auto-Sync**: Valid key automatically flows to the FRED Series widget

### Overview Tab  

1. **Multi-Series Input**: Select one or more FRED series IDs (e.g., `RPI,PCE,UNRATE`)
2. **Date Selection**: Choose start date for historical data
3. **Visualization**: Data displays as interactive table with chart toggle
4. **Chart Features**: Line chart optimized for time series with proper date axis

## Example Series IDs

| Series ID | Description | Data Type |
|-----------|-------------|-----------|
| `SP500` | S&P 500 Stock Price Index | Financial |
| `GDP` | Gross Domestic Product | Economic Output |
| `UNRATE` | Unemployment Rate | Labor Market |
| `FEDFUNDS` | Federal Funds Rate | Monetary Policy |
| `CPIAUCSL` | Consumer Price Index | Inflation |
| `RPI` | Real Personal Income | Economic Indicator |
| `PCE` | Personal Consumption Expenditures | Economic Activity |

## Getting Your FRED API Key

1. Visit: https://fred.stlouisfed.org/docs/api/api_key.html
2. Create a free account with the Federal Reserve Bank of St. Louis
3. Generate your API key
4. Enter it in the "API Key" tab of the OpenBB Workspace app
