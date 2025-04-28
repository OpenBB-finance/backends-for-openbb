import json
from pathlib import Path
from textwrap import dedent
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

## example of markdown widget 
@app.get("/defi_llama_protocol_details")
def defi_llama_protocol_details(protocol_id: str = None):
    """Get details for a given protocol using Defi Llama"""
    data = requests.get(f'https://api.llama.fi/protocol/{protocol_id}')

    if data.status_code == 200:
        data = data.json()
    else:
        return JSONResponse(content={"error": data.text}, status_code=data.status_code)
    
    github_links = ""
    if 'github' in data and data['github']:
        github_links = "**GitHub:** " + ", ".join(data['github'])

    # Use HTML for multi-column layout
    markdown = dedent(f"""
        ![{data.get('name', 'N/A')} Logo]({data.get('logo', '')}) 

        # {data.get('name', 'N/A')} ({data.get('symbol', 'N/A').upper()})

        **Description:** {data.get('description', 'N/A')}

        ---

        ## Twitter

        **Twitter:** {data.get('twitter', 'N/A')}

        ## Links

        **Website:** {data.get('url', 'N/A')}

        {github_links}
    """)
    return markdown