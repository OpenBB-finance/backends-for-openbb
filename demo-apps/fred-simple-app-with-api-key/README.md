# FRED Series Widget

A simple OpenBB Workspace widget for fetching and displaying Federal Reserve Economic Data (FRED) series.

## Setup

1. Set your FRED API key as an environment variable:
   ```bash
   export FRED_API_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## Usage

The widget provides:
- **Series ID**: Text input for the FRED series identifier (e.g., SP500, GDP, UNRATE)
- **Start Date**: Date picker for selecting the start date of data retrieval

## Example Series IDs

- `SP500` - S&P 500 Stock Price Index
- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `FEDFUNDS` - Federal Funds Rate
- `CPIAUCSL` - Consumer Price Index

## API Endpoints

- `/` - Root endpoint with basic info
- `/widgets.json` - Widget configuration
- `/apps.json` - App configuration  
- `/fred_series` - Main endpoint that fetches FRED data

## FRED API Key

Get your free API key from: https://fred.stlouisfed.org/docs/api/api_key.html