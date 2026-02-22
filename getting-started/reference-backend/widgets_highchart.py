import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from highcharts_core.chart import Chart

from core import register_widget

router = APIRouter()


@register_widget({
    "name": "Chains TVL Highcharts",
    "description": "Get current TVL of all chains using Defi Llama and plot with Highcharts",
    "category": "crypto",
    "type": "chart-highcharts",
    "endpoint": "chains_highchart",
    "gridData": {"w": 20, "h": 9}
})
@router.get("/chains_highchart")
def get_chains_highchart(theme: str = "dark"):
    """Get current TVL of all chains using Defi Llama"""
    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        chains = response.json()

        # Sort by TVL and get top 30
        top_30 = sorted(chains, key=lambda x: x.get('tvl', 0), reverse=True)[:30]

        # Extract categories and format TVL values (in billions)
        categories = [chain['name'] for chain in top_30]
        data = [round(chain['tvl'] / 1e9, 2) for chain in top_30]

        # Configure chart options with theme support
        chart_options = {
            'chart': {
                'type': 'column',
                'backgroundColor': 'transparent'
            },
            'title': {'text': 'Top 30 Chains by TVL'},
            'xAxis': {
                'categories': categories,
                'title': {'text': 'Chain Name'},
                'labels': {
                    'style': {
                        'color': '#ffffff' if theme == 'dark' else '#000000'
                    }
                }
            },
            'yAxis': {
                'title': {'text': 'Total Value Locked (TVL in billions $)'},
                'labels': {
                    'style': {
                        'color': '#ffffff' if theme == 'dark' else '#000000'
                    }
                }
            },
            'tooltip': {
                'pointFormat': '<b>${point.y:.2f}B</b>'
            },
            'series': [{
                'name': 'Chain',
                'data': data
            }]
        }

        # Apply theme-specific styling
        if theme == 'dark':
            chart_options.update({
                'title': {'text': 'Top 30 Chains by TVL', 'style': {'color': '#ffffff'}},
                'legend': {'itemStyle': {'color': '#ffffff'}},
                'xAxis': {
                    **chart_options['xAxis'],
                    'title': {'text': 'Chain Name', 'style': {'color': '#ffffff'}},
                    'lineColor': '#555555',
                    'tickColor': '#555555'
                },
                'yAxis': {
                    **chart_options['yAxis'],
                    'title': {'text': 'Total Value Locked (TVL in billions $)', 'style': {'color': '#ffffff'}},
                    'gridLineColor': '#333333'
                },
                'plotOptions': {
                    'series': {
                        'color': '#3498db'
                    }
                }
            })
        else:
            chart_options.update({
                'title': {'text': 'Top 30 Chains by TVL', 'style': {'color': '#333333'}},
                'legend': {'itemStyle': {'color': '#333333'}},
                'xAxis': {
                    **chart_options['xAxis'],
                    'title': {'text': 'Chain Name', 'style': {'color': '#333333'}},
                    'lineColor': '#cccccc',
                    'tickColor': '#cccccc'
                },
                'yAxis': {
                    **chart_options['yAxis'],
                    'title': {'text': 'Total Value Locked (TVL in billions $)', 'style': {'color': '#333333'}},
                    'gridLineColor': '#e6e6e6'
                },
                'plotOptions': {
                    'series': {
                        'color': '#2980b9'
                    }
                }
            })

        chart = Chart.from_options(chart_options)
        return chart.to_dict()

    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )
