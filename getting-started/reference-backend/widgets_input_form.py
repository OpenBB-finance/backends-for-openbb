from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import register_widget, WIDGETS

router = APIRouter()

# Global variable to store form submissions
# This acts as a simple in-memory database for our form entries
ALL_FORMS = []

@router.post("/form_submit")
async def form_submit(params: dict) -> JSONResponse:
    """
    Handle form submissions for both adding and updating records.

    This endpoint receives form data and performs validation before processing.
    It supports both adding new records and updating existing ones.
    """
    global ALL_FORMS

    # Validate required fields
    if not params.get("client_first_name") or not params.get("client_last_name"):
        return JSONResponse(
            status_code=400,
            content={"error": "Client first name and last name are required"},
        )

    if not params.get("investment_types") or not params.get("risk_profile"):
        return JSONResponse(
            status_code=400,
            content={"error": "Investment types and risk profile are required"},
        )

    # Handle form submission based on the action (add or update)
    add_record = params.pop("add_record", None)
    if add_record:
        ALL_FORMS.append(
            {k: ",".join(v) if isinstance(v, list) else v for k, v in params.items()}
        )

    update_record = params.pop("update_record", None)
    if update_record:
        for record in ALL_FORMS:
            if record["client_first_name"] == params.get(
                "client_first_name"
            ) and record["client_last_name"] == params.get("client_last_name"):
                record.update(params)

    return JSONResponse(content={"success": True})


@register_widget({
    "name": "Entry Form",
    "description": "Example of a more complex entry form",
    "category": "forms",
    "subCategory": "form",
    "endpoint": "all_forms",
    "type": "table",
    "gridData": {"w": 20, "h": 9},
    "params": [{
        "paramName": "form",
        "description": "Form example",
        "type": "form",
        "endpoint": "form_submit",
        "inputParams": [
            {
                "paramName": "client_first_name",
                "type": "text",
                "value": "",
                "label": "First Name",
                "description": "Client's first name",
            },
            {
                "paramName": "client_last_name",
                "type": "text",
                "value": "",
                "label": "Last Name",
                "description": "Client's last name",
            },
            {
                "paramName": "investment_types",
                "type": "text",
                "value": None,
                "label": "Investment Types",
                "description": "Selected investment vehicles",
                "multiSelect": True,
                "options": [
                    {"label": "Stocks", "value": "stocks"},
                    {"label": "Bonds", "value": "bonds"},
                    {"label": "Mutual Funds", "value": "mutual_funds"},
                    {"label": "ETFs", "value": "etfs"},
                ],
            },
            {
                "paramName": "risk_profile",
                "type": "text",
                "value": "",
                "label": "Risk Profile",
                "description": "Client risk tolerance assessment",
            },
            {
                "paramName": "add_record",
                "type": "button",
                "value": True,
                "label": "Add Client",
                "description": "Add client record",
            },
            {
                "paramName": "update_record",
                "type": "button",
                "value": True,
                "label": "Update Client",
                "description": "Update client record",
            },
        ],
    }],
})
@router.get("/all_forms")
async def all_forms() -> list:
    """
    Returns all form submissions.

    This GET endpoint is called by the OpenBB widget after form submission.
    The widget refresh mechanism works by:
    1. User submits form (POST to /form_submit)
    2. If POST returns 200, widget automatically refreshes
    3. Widget refresh calls this GET endpoint to fetch updated data
    """
    return (
        ALL_FORMS
        if ALL_FORMS
        else [
            {
                "client_first_name": None,
                "client_last_name": None,
                "investment_types": None,
                "risk_profile": None,
            }
        ]
    )
