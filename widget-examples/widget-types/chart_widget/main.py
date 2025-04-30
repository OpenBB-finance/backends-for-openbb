import json
from pathlib import Path
import pandas as pd
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly_templates import dark_template

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:1420"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


# Example of a Build in chart widget
@app.get("/chains_table")
def chains_table():
    """Get current TVL of all chains using Defi LLama"""
    params = {}
    response = requests.get("https://api.llama.fi/v2/chains", params=params)

    if response.status_code == 200:
        return response.json()

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )


# Example of a Highchart chart widget
@app.get("/chains-highchart")
def get_chains_highchart():
    """Get current TVL of all chains using Defi Llama"""
    import requests
    import pandas as pd
    from fastapi.responses import JSONResponse
    from highcharts_core.chart import Chart

    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        top_30_df = df.sort_values(by='tvl', ascending=False).head(30)
        
        # Format TVL values to be more readable (in billions)
        top_30_df['formatted_tvl'] = top_30_df['tvl'].apply(lambda x: round(x / 1e9, 2))

        categories = top_30_df['name'].tolist()
        data = top_30_df['formatted_tvl'].tolist()

        chart_options = {
            'chart': {'type': 'column', 'height': "50%"},
            'title': {'text': 'Top 30 Chains by TVL'},
            'xAxis': {'categories': categories, 'title': {'text': 'Chain Name'}},
            'yAxis': {'title': {'text': 'Total Value Locked (TVL in billions $)'}},
            'tooltip': {
                'pointFormat': '<b>${point.y:.2f}B</b>'
            },
            'series': [{
                'name': 'Chain',
                'data': data
            }]
        }

        chart = Chart.from_options(chart_options)

        return chart.to_dict()

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

# Example of a Plotly chart widget
@app.get("/chains")
def get_chains():
    """Get current TVL of all chains using Defi LLama"""
    params = {}
    response = requests.get("https://api.llama.fi/v2/chains", params=params)

    if response.status_code == 200:
        # Create a DataFrame from the JSON data
        df = pd.DataFrame(response.json())

        # Sort the DataFrame by 'tvl' in descending order and select the top 30
        top_30_df = df.sort_values(by='tvl', ascending=False).head(30)

        # Create a bar chart using Plotly
        figure = go.Figure(
            data=[go.Bar(x=top_30_df["tokenSymbol"], y=top_30_df["tvl"])],
            # Apply the dark template - see plotly_templates.py
            layout=go.Layout(
                template=dark_template,
                title="Top 30 Chains by TVL",
                xaxis_title="Token Symbol",
                yaxis_title="Total Value Locked (TVL)"
            )
        )

        # return the plotly json
        return json.loads(figure.to_json())

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )