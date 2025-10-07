# Import required libraries
import json
import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fredapi import Fred
import pandas as pd
import numpy as np


# Initialize FastAPI application with metadata
app = FastAPI(
    title="FRED Series Widget",
    description="Simple FRED Series widget for OpenBB Workspace",
    version="0.0.1"
)

# Configure CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "FRED Series Widget"}


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


@app.get("/fred_series")
def fred_series(series_id: str = "SP500", start_date: str = "2020-01-01", api_key: str = ""):
    """Fetch FRED series data and return as a table.
    
    Args:
        series_id (str): FRED series ID(s), comma-separated (default: SP500)
        start_date (str): Start date in YYYY-MM-DD format (default: 2020-01-01)
        api_key (str): FRED API key (optional, overrides environment variable)
    
    Returns:
        list: Array of records with date and series values
    """
    try:
        # Use provided API key or fall back to environment variable
        if not api_key:
            api_key = os.getenv('FRED_API_KEY')
        
        if not api_key:
            raise HTTPException(status_code=400, detail="FRED API key required: provide via parameter or set FRED_API_KEY environment variable")
        
        fred = Fred(api_key=api_key)
        
        # Validate and parse start date
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        # Parse multiple series IDs
        series_ids = [sid.strip() for sid in series_id.split(',') if sid.strip()]
        
        if not series_ids:
            raise HTTPException(status_code=400, detail="At least one series ID is required")
        
        # Fetch data for all series
        all_series_data = {}
        for sid in series_ids:
            try:
                data = fred.get_series(sid, observation_start=start_date)
                if not data.empty:
                    all_series_data[sid] = data
            except Exception as e:
                # Continue with other series if one fails
                print(f"Failed to fetch {sid}: {e}")
                continue
        
        if not all_series_data:
            raise HTTPException(status_code=404, detail=f"No data found for any of the series: {', '.join(series_ids)}")
        
        # Combine all series into a single DataFrame
        df_list = []
        for sid, data in all_series_data.items():
            temp_df = data.to_frame(name=sid)
            df_list.append(temp_df)
        
        # Merge all series on date index
        combined_df = df_list[0]
        for df_item in df_list[1:]:
            combined_df = combined_df.join(df_item, how='outer')
        
        # Reset index and format date
        combined_df = combined_df.reset_index()
        # The index column might be named differently, let's ensure it's called 'Date'
        if 'Date' not in combined_df.columns:
            # Find the date column (should be the first column after reset_index)
            date_col = combined_df.columns[0]
            combined_df = combined_df.rename(columns={date_col: 'Date'})
        
        combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.strftime('%Y-%m-%d')
        
        # Handle NaN and inf values for all series columns
        for col in combined_df.columns:
            if col != 'Date':
                combined_df[col] = combined_df[col].replace([float('inf'), float('-inf')], None)
                combined_df[col] = combined_df[col].where(pd.notna(combined_df[col]), None)
        
        # Convert to records with explicit handling of problematic values
        records = []
        for _, row in combined_df.iterrows():
            record = {"Date": row['Date']}
            for col in combined_df.columns:
                if col != 'Date':
                    value = row[col]
                    if value is None or pd.isna(value):
                        value = None
                    elif isinstance(value, (int, float)) and not np.isfinite(value):
                        value = None
                    record[col] = value
            records.append(record)
        
        # Return simple array of records for AgGrid with columnsDefs
        return records
        
    except Exception as e:
        print(f"Error in fred_series: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing FRED data: {str(e)}")