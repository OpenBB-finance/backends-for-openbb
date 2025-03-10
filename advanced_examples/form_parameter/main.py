import json
from pathlib import Path
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:1420",
    "http://localhost:5050",
    "https://pro.openbb.dev",
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "https://excel.openbb.dev",
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


ALL_FORMS = []

# Submit form endpoint to handle the form submission
@app.post("/form_submit")
async def form_submit(params: dict) -> JSONResponse:
    global ALL_FORMS
    
    # Check if first name and last name are provided
    if not params.get("client_first_name") or not params.get("client_last_name"):
        # IMPORTANT: Even with a 400 status code, the error message is passed to the frontend
        # and can be displayed to the user in the OpenBB widget
        return JSONResponse(
            status_code=400,
            content={"error": "Client first name and last name are required"}
        )
    
    # Check if investment types and risk profile are provided
    if not params.get("investment_types") or not params.get("risk_profile"):
        return JSONResponse(
            status_code=400,
            content={"error": "Investment types and risk profile are required"}
        )

    # Check if add_record or update_record is provided
    add_record = params.pop("add_record", None)
    if add_record:
        ALL_FORMS.append(
            {k: ",".join(v) if isinstance(v, list) else v for k, v in params.items()}
        )
    update_record = params.pop("update_record", None)
    if update_record:
        for record in ALL_FORMS:
            if record["client_first_name"] == params.get("client_first_name") and record[
                "client_last_name"
            ] == params.get("client_last_name"):
                record.update(params)
    
    # IMPORTANT: The OpenBB Workspace only checks for a 200 status code from this endpoint
    # The actual content returned doesn't matter for the widget refresh mechanism
    # After a successful submission, Workspace will automatically refresh the widget
    # by calling the GET endpoint defined in the widget configuration
    return JSONResponse(content={"success": True})


# Get all forms
@app.get("/all_forms")
async def all_forms() -> list:
    print(ALL_FORMS)
    # IMPORTANT: This GET endpoint is called by the OpenBB widget after form submission
    # The widget refresh mechanism works by:
    # 1. User submits form (POST to /form_submit)
    # 2. If POST returns 200, widget automatically refreshes
    # 3. Widget refresh calls this GET endpoint to fetch updated data
    # 4. This function must return ALL data needed to display the updated widget
    return (
        ALL_FORMS
        if ALL_FORMS
        else [
            {"client_first_name": None, "client_last_name": None, "investment_types": None, "risk_profile": None}
        ]
    )