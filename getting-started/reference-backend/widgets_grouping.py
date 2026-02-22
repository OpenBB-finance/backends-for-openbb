from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Query

from core import register_widget, WIDGETS, FileOption

router = APIRouter()


@router.get("/company_options")
def get_company_options():
    """Returns a list of available car manufacturers"""
    return [
        {"label": "Toyota Motor Corporation", "value": "TM"},
        {"label": "Volkswagen Group", "value": "VWAGY"},
        {"label": "General Motors", "value": "GM"},
        {"label": "Ford Motor Company", "value": "F"},
        {"label": "Tesla Inc.", "value": "TSLA"}
    ]


@register_widget({
    "name": "Car Manufacturer Details",
    "description": "Displays detailed information about the selected car manufacturer",
    "type": "markdown",
    "endpoint": "company_details",
    "gridData": {"w": 16, "h": 8},
    "params": [
        {
            "paramName": "company",  # Shared paramName with company_performance widget
            "description": "Select a car manufacturer to view details",
            "value": "TM",
            "label": "Manufacturer",
            "type": "endpoint",
            "optionsEndpoint": "/company_options"  # Shared endpoint with company_performance widget
        },
        {
            "paramName": "year",  # Shared paramName with company_performance widget
            "description": "Select model year to view details",
            "value": "2024",
            "label": "Model Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"}
            ]
        }
    ]
})
@router.get("/company_details")
def get_company_details(company: str, year: str = "2024"):
    """Returns car manufacturer details in markdown format"""
    company_info = {
        "TM": {
            "name": "Toyota Motor Corporation",
            "sector": "Automotive",
            "market_cap": "280B",
            "pe_ratio": 9.5,
            "dividend_yield": 2.1,
            "description": "Toyota Motor Corporation designs, manufactures, assembles, and sells passenger vehicles, minivans, commercial vehicles, and related parts and accessories worldwide.",
            "models": {
                "2024": ["Camry", "Corolla", "RAV4", "Highlander"],
                "2023": ["Camry", "Corolla", "RAV4", "Highlander"],
                "2022": ["Camry", "Corolla", "RAV4", "Highlander"]
            }
        },
        "VWAGY": {
            "name": "Volkswagen Group",
            "sector": "Automotive",
            "market_cap": "75B",
            "pe_ratio": 4.2,
            "dividend_yield": 3.5,
            "description": "Volkswagen Group manufactures and sells automobiles worldwide. The company offers passenger cars, commercial vehicles, and power engineering systems.",
            "models": {
                "2024": ["Golf", "Passat", "Tiguan", "ID.4"],
                "2023": ["Golf", "Passat", "Tiguan", "ID.4"],
                "2022": ["Golf", "Passat", "Tiguan", "ID.4"]
            }
        },
        "GM": {
            "name": "General Motors",
            "sector": "Automotive",
            "market_cap": "45B",
            "pe_ratio": 5.8,
            "dividend_yield": 1.2,
            "description": "General Motors designs, builds, and sells cars, trucks, crossovers, and automobile parts worldwide.",
            "models": {
                "2024": ["Silverado", "Equinox", "Malibu", "Corvette"],
                "2023": ["Silverado", "Equinox", "Malibu", "Corvette"],
                "2022": ["Silverado", "Equinox", "Malibu", "Corvette"]
            }
        },
        "F": {
            "name": "Ford Motor Company",
            "sector": "Automotive",
            "market_cap": "48B",
            "pe_ratio": 7.2,
            "dividend_yield": 4.8,
            "description": "Ford Motor Company designs, manufactures, markets, and services a line of Ford trucks, cars, sport utility vehicles, electrified vehicles, and Lincoln luxury vehicles.",
            "models": {
                "2024": ["F-150", "Mustang", "Explorer", "Mach-E"],
                "2023": ["F-150", "Mustang", "Explorer", "Mach-E"],
                "2022": ["F-150", "Mustang", "Explorer", "Mach-E"]
            }
        },
        "TSLA": {
            "name": "Tesla Inc.",
            "sector": "Automotive",
            "market_cap": "800B",
            "pe_ratio": 65.3,
            "dividend_yield": 0.0,
            "description": "Tesla Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally.",
            "models": {
                "2024": ["Model 3", "Model Y", "Model S", "Model X"],
                "2023": ["Model 3", "Model Y", "Model S", "Model X"],
                "2022": ["Model 3", "Model Y", "Model S", "Model X"]
            }
        }
    }

    details = company_info.get(company, {
        "name": "Unknown",
        "sector": "Unknown",
        "market_cap": "N/A",
        "pe_ratio": 0,
        "dividend_yield": 0,
        "description": "No information available for this manufacturer.",
        "models": {"2024": [], "2023": [], "2022": []}
    })

    models = details['models'].get(year, [])

    return f"""# {details['name']} ({company}) - {year} Models
**Sector:** {details['sector']}
**Market Cap:** ${details['market_cap']}
**P/E Ratio:** {details['pe_ratio']}
**Dividend Yield:** {details['dividend_yield']}%

{details['description']}

## {year} Model Lineup
{', '.join(models)}
"""


@register_widget({
    "name": "Car Manufacturer Performance",
    "description": "Displays performance metrics for the selected car manufacturer",
    "type": "table",
    "endpoint": "company_performance",
    "gridData": {"w": 16, "h": 8},
    "params": [
        {
            "paramName": "company",  # Shared paramName with company_details widget
            "description": "Select a car manufacturer to view performance",
            "value": "TM",
            "label": "Manufacturer",
            "type": "endpoint",
            "optionsEndpoint": "/company_options"  # Shared endpoint with company_details widget
        },
        {
            "paramName": "year",  # Shared paramName with company_details widget
            "description": "Select model year to view performance",
            "value": "2024",
            "label": "Model Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"}
            ]
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "metric",
                    "headerName": "Metric",
                    "cellDataType": "text",
                    "width": 150
                },
                {
                    "field": "value",
                    "headerName": "Value",
                    "cellDataType": "text",
                    "width": 150
                },
                {
                    "field": "change",
                    "headerName": "Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 150
                }
            ]
        }
    }
})
@router.get("/company_performance")
def get_company_performance(company: str, year: str = "2024"):
    """Returns car manufacturer performance metrics"""
    performance_data = {
        "TM": {
            "2024": [
                {"metric": "Global Sales", "value": "10.5M", "change": 5.2},
                {"metric": "EV Sales", "value": "1.2M", "change": 45.8},
                {"metric": "Operating Margin", "value": "8.5%", "change": 1.2},
                {"metric": "R&D Investment", "value": "$12.5B", "change": 15.3}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "9.98M", "change": 3.1},
                {"metric": "EV Sales", "value": "0.82M", "change": 35.2},
                {"metric": "Operating Margin", "value": "7.3%", "change": 0.8},
                {"metric": "R&D Investment", "value": "$10.8B", "change": 12.5}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "9.67M", "change": 1.2},
                {"metric": "EV Sales", "value": "0.61M", "change": 25.4},
                {"metric": "Operating Margin", "value": "6.5%", "change": -0.5},
                {"metric": "R&D Investment", "value": "$9.6B", "change": 8.7}
            ]
        },
        "VWAGY": {
            "2024": [
                {"metric": "Global Sales", "value": "9.2M", "change": 4.8},
                {"metric": "EV Sales", "value": "1.5M", "change": 52.3},
                {"metric": "Operating Margin", "value": "7.8%", "change": 1.5},
                {"metric": "R&D Investment", "value": "$15.2B", "change": 18.5}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "8.78M", "change": 3.2},
                {"metric": "EV Sales", "value": "0.98M", "change": 42.1},
                {"metric": "Operating Margin", "value": "6.3%", "change": 0.9},
                {"metric": "R&D Investment", "value": "$12.8B", "change": 15.2}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "8.5M", "change": 1.8},
                {"metric": "EV Sales", "value": "0.69M", "change": 32.5},
                {"metric": "Operating Margin", "value": "5.4%", "change": -0.7},
                {"metric": "R&D Investment", "value": "$11.1B", "change": 10.8}
            ]
        },
        "GM": {
            "2024": [
                {"metric": "Global Sales", "value": "6.8M", "change": 3.5},
                {"metric": "EV Sales", "value": "0.8M", "change": 48.2},
                {"metric": "Operating Margin", "value": "8.2%", "change": 1.8},
                {"metric": "R&D Investment", "value": "$9.5B", "change": 16.5}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "6.57M", "change": 2.1},
                {"metric": "EV Sales", "value": "0.54M", "change": 38.5},
                {"metric": "Operating Margin", "value": "6.4%", "change": 1.2},
                {"metric": "R&D Investment", "value": "$8.15B", "change": 14.2}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "6.43M", "change": 0.8},
                {"metric": "EV Sales", "value": "0.39M", "change": 28.7},
                {"metric": "Operating Margin", "value": "5.2%", "change": -0.5},
                {"metric": "R&D Investment", "value": "$7.13B", "change": 9.8}
            ]
        },
        "F": {
            "2024": [
                {"metric": "Global Sales", "value": "4.2M", "change": 2.8},
                {"metric": "EV Sales", "value": "0.6M", "change": 42.5},
                {"metric": "Operating Margin", "value": "7.5%", "change": 1.5},
                {"metric": "R&D Investment", "value": "$8.2B", "change": 15.8}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "4.08M", "change": 1.5},
                {"metric": "EV Sales", "value": "0.42M", "change": 35.2},
                {"metric": "Operating Margin", "value": "6.0%", "change": 1.0},
                {"metric": "R&D Investment", "value": "$7.08B", "change": 13.5}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "4.02M", "change": 0.5},
                {"metric": "EV Sales", "value": "0.31M", "change": 25.8},
                {"metric": "Operating Margin", "value": "5.0%", "change": -0.8},
                {"metric": "R&D Investment", "value": "$6.24B", "change": 8.9}
            ]
        },
        "TSLA": {
            "2024": [
                {"metric": "Global Sales", "value": "2.1M", "change": 35.2},
                {"metric": "EV Sales", "value": "2.1M", "change": 35.2},
                {"metric": "Operating Margin", "value": "15.5%", "change": 3.7},
                {"metric": "R&D Investment", "value": "$4.5B", "change": 25.8}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "1.55M", "change": 28.5},
                {"metric": "EV Sales", "value": "1.55M", "change": 28.5},
                {"metric": "Operating Margin", "value": "11.8%", "change": 2.5},
                {"metric": "R&D Investment", "value": "$3.58B", "change": 22.3}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "1.21M", "change": 21.8},
                {"metric": "EV Sales", "value": "1.21M", "change": 21.8},
                {"metric": "Operating Margin", "value": "9.3%", "change": 1.8},
                {"metric": "R&D Investment", "value": "$2.93B", "change": 18.5}
            ]
        }
    }

    return performance_data.get(company, {}).get(year, [
        {"metric": "No Data", "value": "N/A", "change": 0}
    ])


@router.get("/get_tickers_list")
def get_tickers_list():
    """Returns a list of available stock symbols"""
    return [
        {"label": "Apple Inc.", "value": "AAPL"},
        {"label": "Microsoft Corporation", "value": "MSFT"},
        {"label": "Google", "value": "GOOGL"},
        {"label": "Amazon", "value": "AMZN"},
        {"label": "Tesla", "value": "TSLA"}
    ]

@register_widget({
    "name": "Table widget with grouping by cell click",
    "description": "A table widget that groups data when clicking on symbols. Click on a symbol to update all related widgets.",
    "type": "table",
    "endpoint": "table_widget_with_grouping_by_cell_click",
    "params": [
        {
            "paramName": "symbol",  # This parameter name is crucial - it's used for grouping
            "description": "Select stocks to display",
            "value": "AAPL",
            "label": "Symbol",
            "type": "endpoint",
            "optionsEndpoint": "/get_tickers_list",
            "multiSelect": False,
            "show": True
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "cellDataType": "text",
                    "width": 120,
                    "pinned": "left",
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupBy": {
                            "paramName": "symbol"
                        }
                    }
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                    "formatterFn": "none",
                    "width": 120
                },
                {
                    "field": "change",
                    "headerName": "Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 120
                },
                {
                    "field": "volume",
                    "headerName": "Volume",
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "width": 150
                }
            ]
        }
    },
    "gridData": {
        "w": 20,
        "h": 9
    }
})
@router.get("/table_widget_with_grouping_by_cell_click")
def table_widget_with_grouping_by_cell_click():
    """Returns stock data for the table - shows all rows, clicking updates other widgets via groupBy"""
    return [
        {"symbol": "AAPL", "price": 150.25, "change": 2.5, "volume": 45000000},
        {"symbol": "MSFT", "price": 350.50, "change": 1.8, "volume": 32000000},
        {"symbol": "GOOGL", "price": 140.75, "change": -0.5, "volume": 28000000},
        {"symbol": "AMZN", "price": 178.25, "change": 3.2, "volume": 38000000},
        {"symbol": "TSLA", "price": 245.80, "change": -1.2, "volume": 52000000}
    ]

@register_widget({
    "name": "Widget managed by parameter from cell click on table widget",
    "description": "This widget demonstrates how to use the grouped symbol parameter from a table widget. When a symbol is clicked in the table, this widget will automatically update to show details for the selected symbol.",
    "type": "markdown",
    "endpoint": "widget_managed_by_parameter_from_cell_click_on_table_widget",
    "params": [
        {
            "paramName": "symbol",  # Must match the groupBy.paramName in the table widget
            "description": "The symbol to get details for",
            "value": "AAPL",
            "label": "Symbol",
            "type": "endpoint",
            "optionsEndpoint": "/get_tickers_list",
            "show": True
        }
    ],
    "gridData": {
        "w": 20,
        "h": 6
    }
})
@router.get("/widget_managed_by_parameter_from_cell_click_on_table_widget")
def widget_managed_by_parameter_from_cell_click_on_table_widget(symbol: str = "AAPL"):
    """Returns markdown details for the selected symbol"""
    stock_info = {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "market_cap": "2.8T", "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."},
        "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "market_cap": "2.9T", "description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide."},
        "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "market_cap": "1.9T", "description": "Alphabet Inc. offers various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America."},
        "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "market_cap": "1.9T", "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions through online and physical stores."},
        "TSLA": {"name": "Tesla Inc.", "sector": "Automotive", "market_cap": "780B", "description": "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems."}
    }
    info = stock_info.get(symbol, stock_info["AAPL"])
    return f"""# {info['name']} ({symbol})

**Sector:** {info['sector']}
**Market Cap:** ${info['market_cap']}

{info['description']}
"""

@register_widget({
    "name": "Company List with ID Mapping",
    "description": "Table showing company names but passing IDs on click",
    "type": "table",
    "endpoint": "company_list",
    "params": [
        {
            "paramName": "companyId",  # Parameter expects ID, not name
            "description": "Company identifier",
            "value": "AAPL",
            "label": "Company ID",
            "type": "endpoint",
            "optionsEndpoint": "/company_options",
            "show": True
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "companyName",  # Display name in cell
                    "headerName": "Company",
                    "cellDataType": "text",
                    "width": 200,
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupBy": {
                            "paramName": "companyId",
                            "valueField": "companyId"  # Use ID field instead of companyName
                        }
                    }
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                    "formatterFn": "none",
                    "width": 120
                }
            ]
        }
    }
})

@router.get("/company_list")
def get_company_list():
    return [
        {
            "companyName": "Apple Inc.",      # Displayed in cell
            "companyId": "AAPL",              # Passed to parameter
            "price": 150.25
        },
        {
            "companyName": "Microsoft Corporation",
            "companyId": "MSFT",
            "price": 350.50
        }
    ]
