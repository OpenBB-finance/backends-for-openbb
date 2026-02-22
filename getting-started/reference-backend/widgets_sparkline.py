from fastapi import APIRouter

from core import register_widget, WIDGETS

router = APIRouter()

@register_widget({
    "name": "Table Widget with Basic Sparklines",
    "description": "A table widget with basic sparklines showing min/max points",
    "type": "table",
    "endpoint": "table_widget_basic_sparklines",
    "gridData": {"w": 20, "h": 6},
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "stock", "headerName": "Stock", "cellDataType": "text", "width": 120, "pinned": "left"},
                {
                    "field": "price_history",
                    "headerName": "Price History",
                    "width": 200,
                    "sparkline": {
                        "type": "line",
                        "options": {
                            "stroke": "#2563eb",
                            "strokeWidth": 2,
                            "markers": {"enabled": True, "size": 3},
                            "pointsOfInterest": {
                                "maximum": {"fill": "#22c55e", "stroke": "#16a34a", "size": 6},
                                "minimum": {"fill": "#ef4444", "stroke": "#dc2626", "size": 6},
                            },
                        },
                    },
                },
                {
                    "field": "volume",
                    "headerName": "Volume",
                    "width": 150,
                    "sparkline": {
                        "type": "bar",
                        "options": {
                            "fill": "#6b7280",
                            "stroke": "#4b5563",
                            "pointsOfInterest": {
                                "maximum": {"fill": "#22c55e", "stroke": "#16a34a"},
                                "minimum": {"fill": "#ef4444", "stroke": "#dc2626"},
                            },
                        },
                    },
                },
            ]
        }
    },
})
@router.get("/table_widget_basic_sparklines")
def table_widget_basic_sparklines():
    """Returns mock data with sparklines"""
    return [
        {"stock": "AAPL", "price_history": [150, 155, 148, 162, 158, 165, 170], "volume": [1000, 1200, 900, 1500, 1100, 1300, 1800]},
        {"stock": "GOOGL", "price_history": [2800, 2750, 2900, 2850, 2950, 3000, 2980], "volume": [800, 950, 700, 1200, 850, 1100, 1400]},
        {"stock": "MSFT", "price_history": [340, 335, 350, 345, 360, 355, 365], "volume": [900, 1100, 800, 1300, 950, 1200, 1600]},
    ]


@register_widget({
    "name": "Stock Sparkline Data - With Min/Max Points",
    "description": "Display stock data with sparkline charts highlighting minimum and maximum values",
    "category": "Widgets",
    "subCategory": "sparkline",
    "defaultViz": "table",
    "endpoint": "sparkline",
    "gridData": {"w": 18, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Symbol", "field": "symbol", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Company Name", "field": "name", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Last Price", "field": "lastPrice", "cellDataType": "text", "chartDataType": "series"},
                {"headerName": "Market Cap", "field": "marketCap", "cellDataType": "number", "chartDataType": "series"},
                {"headerName": "Volume", "field": "volume", "cellDataType": "number", "chartDataType": "series"},
                {"headerName": "Sector", "field": "sector", "cellDataType": "text", "chartDataType": "category"},
                {
                    "headerName": "Rate of Change Trend",
                    "field": "rateOfChange",
                    "cellDataType": "object",
                    "chartDataType": "excluded",
                    "sparkline": {
                        "type": "line",
                        "options": {
                            "fill": "rgba(34, 197, 94, 0.2)",
                            "stroke": "#22c55e",
                            "strokeWidth": 2,
                            "tooltip": {"enabled": True},
                            "markers": {"enabled": True, "shape": "circle", "size": 2, "fill": "#22c55e"},
                            "padding": {"top": 5, "right": 5, "bottom": 5, "left": 5},
                            "pointsOfInterest": {
                                "maximum": {"fill": "#ffd700", "stroke": "#ffb000", "strokeWidth": 2, "size": 6},
                                "minimum": {"fill": "#ef4444", "stroke": "#dc2626", "strokeWidth": 2, "size": 6},
                            },
                        },
                    },
                },
            ],
        }
    },
})
@router.get("/sparkline")
async def get_sparkline_data():
    """Get sparkline data for stock symbols - demonstrating min/max points of interest"""
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "lastPrice": "173.50", "marketCap": 2675150000000, "volume": 57807909, "sector": "Technology", "rateOfChange": [2.1, 5.3, -3.2, 8.7, 1.4, -5.1, 12.3, -2.8, 4.6, -1.9]},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "lastPrice": "2891.70", "marketCap": 1834250000000, "volume": 28967543, "sector": "Technology", "rateOfChange": [3.8, -2.1, 6.4, 2.5, -4.3, 9.2, -1.7, 5.1, -6.8, 3.3]},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "lastPrice": "414.67", "marketCap": 3086420000000, "volume": 32145678, "sector": "Technology", "rateOfChange": [1.8, 4.2, -2.9, 3.5, 7.1, -3.4, 2.7, -1.2, 6.8, 0.9]},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "lastPrice": "3307.04", "marketCap": 1702830000000, "volume": 45678901, "sector": "Consumer Services", "rateOfChange": [5.2, -3.8, 8.1, 1.9, -7.3, 4.6, -2.1, 9.4, -1.5, 3.2]},
        {"symbol": "TSLA", "name": "Tesla Inc.", "lastPrice": "248.42", "marketCap": 788960000000, "volume": 89123456, "sector": "Consumer Durables", "rateOfChange": [8.5, -12.3, 15.7, -4.2, 6.8, -8.9, 11.2, -2.6, 4.1, -6.7]},
        {"symbol": "META", "name": "Meta Platforms Inc.", "lastPrice": "485.34", "marketCap": 1247650000000, "volume": 34567890, "sector": "Technology", "rateOfChange": [6.3, 2.8, -9.1, 4.7, 8.2, -3.5, 1.9, -5.4, 10.6, -2.3]},
        {"symbol": "NFLX", "name": "Netflix Inc.", "lastPrice": "421.73", "marketCap": 187450000000, "volume": 23456789, "sector": "Consumer Services", "rateOfChange": [4.1, -6.8, 9.3, 2.7, -4.9, 7.5, -1.8, 5.6, -8.2, 3.4]},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "lastPrice": "875.28", "marketCap": 2158730000000, "volume": 67890123, "sector": "Technology", "rateOfChange": [12.8, -5.4, 18.2, 7.3, -11.6, 9.1, -3.7, 16.9, -8.2, 5.8]},
    ]


@register_widget({
    "name": "Stock Price Trends - Line Sparklines with First/Last Points",
    "description": "Display stock price trends using line sparklines highlighting first and last points",
    "category": "Widgets",
    "subCategory": "sparkline-line",
    "defaultViz": "table",
    "endpoint": "sparkline-line",
    "gridData": {"w": 16, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Symbol", "field": "symbol", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Company Name", "field": "name", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Current Price", "field": "currentPrice", "cellDataType": "number", "chartDataType": "series"},
                {
                    "headerName": "90-Day Price Trend",
                    "field": "priceTrend",
                    "cellDataType": "object",
                    "chartDataType": "excluded",
                    "sparkline": {
                        "type": "line",
                        "options": {
                            "stroke": "#3b82f6",
                            "strokeWidth": 2,
                            "padding": {"top": 5, "right": 5, "bottom": 5, "left": 5},
                            "markers": {"enabled": True, "size": 2, "fill": "#3b82f6"},
                            "pointsOfInterest": {
                                "firstLast": {"fill": "#8b5cf6", "stroke": "#7c3aed", "strokeWidth": 2, "size": 6}
                            },
                        },
                    },
                },
                {"headerName": "Change %", "field": "changePercent", "cellDataType": "number", "chartDataType": "series"},
            ],
        }
    },
})
@router.get("/sparkline-line")
async def get_line_sparkline_data():
    """Get line sparkline data for stock price trends"""
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "currentPrice": 173.50, "priceTrend": [165.2, 167.1, 169.3, 171.2, 168.9, 170.4, 172.1, 173.5, 175.2, 174.8, 173.1, 173.5], "changePercent": 5.04},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "currentPrice": 2891.70, "priceTrend": [2750.3, 2780.1, 2820.4, 2865.2, 2840.7, 2890.1, 2910.3, 2885.6, 2901.4, 2889.2, 2891.7], "changePercent": 5.14},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "currentPrice": 414.67, "priceTrend": [398.2, 405.3, 411.8, 406.9, 409.7, 412.5, 408.3, 415.1, 418.4, 416.2, 414.7], "changePercent": 4.13},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "currentPrice": 3307.04, "priceTrend": [3180.5, 3210.2, 3245.8, 3201.3, 3230.7, 3275.4, 3290.1, 3315.6, 3298.3, 3307.0], "changePercent": 3.98},
        {"symbol": "TSLA", "name": "Tesla Inc.", "currentPrice": 248.42, "priceTrend": [220.1, 235.6, 242.8, 238.2, 245.9, 251.3, 246.7, 248.4, 252.1, 249.8, 248.4], "changePercent": 12.86},
        {"symbol": "META", "name": "Meta Platforms Inc.", "currentPrice": 485.34, "priceTrend": [461.2, 468.9, 475.3, 472.6, 479.1, 483.7, 481.2, 485.3, 488.9, 486.1, 485.3], "changePercent": 5.24},
        {"symbol": "NFLX", "name": "Netflix Inc.", "currentPrice": 421.73, "priceTrend": [395.8, 402.3, 408.7, 405.2, 412.6, 418.9, 415.3, 421.7, 424.2, 422.8, 421.7], "changePercent": 6.54},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "currentPrice": 875.28, "priceTrend": [789.5, 812.3, 845.6, 863.2, 851.7, 869.4, 872.8, 875.3, 881.2, 878.5, 875.3], "changePercent": 10.86},
    ]


@register_widget({
    "name": "Trading Volume - Area Sparklines",
    "description": "Display trading volume data using area sparklines with maximum point highlighting",
    "category": "Widgets",
    "subCategory": "sparkline-area",
    "defaultViz": "table",
    "endpoint": "sparkline-area",
    "gridData": {"w": 16, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Symbol", "field": "symbol", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Company Name", "field": "name", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Avg Volume (M)", "field": "avgVolume", "cellDataType": "number", "chartDataType": "series"},
                {
                    "headerName": "30-Day Volume Trend",
                    "field": "volumeTrend",
                    "cellDataType": "object",
                    "chartDataType": "excluded",
                    "sparkline": {
                        "type": "area",
                        "options": {
                            "fill": "rgba(34, 197, 94, 0.3)",
                            "stroke": "#22c55e",
                            "strokeWidth": 2,
                            "padding": {"top": 5, "right": 5, "bottom": 5, "left": 5},
                            "markers": {"enabled": True, "size": 2, "fill": "#22c55e"},
                            "pointsOfInterest": {
                                "maximum": {"fill": "#fbbf24", "stroke": "#f59e0b", "strokeWidth": 2, "size": 6}
                            },
                        },
                    },
                },
                {"headerName": "Volume Change %", "field": "volumeChangePercent", "cellDataType": "number", "chartDataType": "series"},
            ],
        }
    },
})
@router.get("/sparkline-area")
async def get_area_sparkline_data():
    """Get area sparkline data for trading volume trends"""
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "avgVolume": 50.2, "volumeTrend": [48.5, 52.1, 49.8, 51.3, 50.9, 48.7, 53.2, 50.2, 49.6, 51.8, 55.3, 52.4], "volumeChangePercent": 3.45},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "avgVolume": 29.0, "volumeTrend": [27.8, 29.5, 28.2, 30.1, 29.0, 27.6, 31.2, 29.8, 28.5, 29.3, 32.1, 30.4], "volumeChangePercent": 4.21},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "avgVolume": 32.1, "volumeTrend": [31.2, 33.1, 32.8, 30.9, 32.1, 33.5, 31.7, 32.4, 33.2, 32.8, 35.2, 33.9], "volumeChangePercent": 2.98},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "avgVolume": 45.7, "volumeTrend": [44.2, 47.3, 45.1, 46.8, 45.7, 44.9, 48.2, 46.5, 45.3, 47.1, 49.8, 47.6], "volumeChangePercent": 3.15},
        {"symbol": "TSLA", "name": "Tesla Inc.", "avgVolume": 89.1, "volumeTrend": [85.6, 92.8, 87.9, 91.2, 89.1, 86.4, 93.5, 88.7, 90.8, 89.5, 96.2, 91.8], "volumeChangePercent": 4.32},
    ]


@register_widget({
    "name": "Quarterly Earnings - Column Sparklines",
    "description": "Display quarterly earnings data using column sparklines",
    "category": "Widgets",
    "subCategory": "sparkline-column",
    "defaultViz": "table",
    "endpoint": "sparkline-column",
    "gridData": {"w": 16, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Symbol", "field": "symbol", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Company Name", "field": "name", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Market Cap", "field": "marketCap", "cellDataType": "number", "chartDataType": "series"},
                {
                    "headerName": "8-Quarter EPS",
                    "field": "quarterlyEps",
                    "cellDataType": "object",
                    "chartDataType": "excluded",
                    "sparkline": {
                        "type": "bar",
                        "options": {
                            "direction": "horizontal",
                            "fill": "#f59e0b",
                            "stroke": "#d97706",
                            "strokeWidth": 1,
                            "padding": {"top": 5, "right": 5, "bottom": 5, "left": 5},
                            "highlightStyle": {"fill": "#fbbf24", "stroke": "#f59e0b"},
                        },
                    },
                },
                {"headerName": "EPS Growth %", "field": "epsGrowth", "cellDataType": "number", "chartDataType": "series"},
            ],
        }
    },
})
@router.get("/sparkline-column")
async def get_column_sparkline_data():
    """Get column sparkline data for quarterly earnings per share"""
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "marketCap": 2675150000000, "quarterlyEps": [1.46, 1.52, 1.29, 1.88, 1.56, 1.64, 1.39, 1.97], "epsGrowth": 6.85},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "marketCap": 1834250000000, "quarterlyEps": [1.05, 1.21, 1.06, 1.33, 1.17, 1.32, 1.15, 1.44], "epsGrowth": 8.57},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "marketCap": 3086420000000, "quarterlyEps": [2.32, 2.45, 2.51, 2.72, 2.48, 2.62, 2.69, 2.93], "epsGrowth": 6.90},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "marketCap": 1702830000000, "quarterlyEps": [0.31, 0.42, 0.52, 0.68, 0.45, 0.58, 0.71, 0.85], "epsGrowth": 25.0},
        {"symbol": "TSLA", "name": "Tesla Inc.", "marketCap": 788960000000, "quarterlyEps": [0.73, 0.85, 1.05, 1.19, 0.91, 1.12, 1.29, 1.45], "epsGrowth": 24.66},
        {"symbol": "META", "name": "Meta Platforms Inc.", "marketCap": 1247650000000, "quarterlyEps": [2.72, 2.88, 3.03, 3.67, 2.98, 3.21, 3.35, 4.01], "epsGrowth": 9.27},
        {"symbol": "NFLX", "name": "Netflix Inc.", "marketCap": 187450000000, "quarterlyEps": [2.80, 3.19, 3.53, 4.28, 3.29, 3.75, 4.13, 4.82], "epsGrowth": 17.50},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "marketCap": 2158730000000, "quarterlyEps": [1.01, 1.36, 2.48, 5.16, 4.28, 6.12, 8.92, 12.96], "epsGrowth": 324.75},
    ]


@register_widget({
    "name": "Monthly Performance - Bar Sparklines with Positive/Negative",
    "description": "Display monthly performance data using bar sparklines with positive/negative styling",
    "category": "Widgets",
    "subCategory": "sparkline-bar",
    "defaultViz": "table",
    "endpoint": "sparkline-bar",
    "gridData": {"w": 16, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Symbol", "field": "symbol", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "Company Name", "field": "name", "cellDataType": "text", "chartDataType": "category"},
                {"headerName": "YTD Return %", "field": "ytdReturn", "cellDataType": "number", "chartDataType": "series"},
                {
                    "headerName": "Monthly Returns",
                    "field": "monthlyReturns",
                    "cellDataType": "object",
                    "chartDataType": "excluded",
                    "sparkline": {
                        "type": "bar",
                        "options": {
                            "direction": "vertical",
                            "xKey": "x",
                            "yKey": "y",
                            "fill": "#8b5cf6",
                            "stroke": "#7c3aed",
                            "strokeWidth": 1,
                            "padding": {"top": 5, "right": 5, "bottom": 5, "left": 5},
                            "pointsOfInterest": {
                                "positiveNegative": {
                                    "positive": {"fill": "#22c55e", "stroke": "#16a34a"},
                                    "negative": {"fill": "#ef4444", "stroke": "#dc2626"},
                                }
                            },
                        },
                    },
                },
                {"headerName": "Best Month %", "field": "bestMonth", "cellDataType": "number", "chartDataType": "series"},
            ],
        }
    },
})
@router.get("/sparkline-bar")
async def get_bar_sparkline_data():
    """Get bar sparkline data for monthly performance returns"""
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "ytdReturn": 15.23, "monthlyReturns": [{"x": "Jan", "y": 2.1}, {"x": "Feb", "y": -1.5}, {"x": "Mar", "y": 3.2}, {"x": "Apr", "y": 1.8}, {"x": "May", "y": -0.7}, {"x": "Jun", "y": 2.8}, {"x": "Jul", "y": 1.2}, {"x": "Aug", "y": -2.1}, {"x": "Sep", "y": 3.5}, {"x": "Oct", "y": 1.7}, {"x": "Nov", "y": 2.3}, {"x": "Dec", "y": 0.9}], "bestMonth": 3.5},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "ytdReturn": 18.67, "monthlyReturns": [{"x": "Jan", "y": 3.2}, {"x": "Feb", "y": 1.8}, {"x": "Mar", "y": -1.2}, {"x": "Apr", "y": 4.1}, {"x": "May", "y": 2.3}, {"x": "Jun", "y": -0.9}, {"x": "Jul", "y": 3.7}, {"x": "Aug", "y": 1.5}, {"x": "Sep", "y": -2.3}, {"x": "Oct", "y": 2.9}, {"x": "Nov", "y": 1.6}, {"x": "Dec", "y": 2.1}], "bestMonth": 4.1},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "ytdReturn": 12.45, "monthlyReturns": [{"x": "Jan", "y": 1.8}, {"x": "Feb", "y": 2.3}, {"x": "Mar", "y": -0.5}, {"x": "Apr", "y": 2.1}, {"x": "May", "y": 1.2}, {"x": "Jun", "y": -1.8}, {"x": "Jul", "y": 2.7}, {"x": "Aug", "y": 0.9}, {"x": "Sep", "y": -1.2}, {"x": "Oct", "y": 2.4}, {"x": "Nov", "y": 1.3}, {"x": "Dec", "y": 1.2}], "bestMonth": 2.7},
        {"symbol": "TSLA", "name": "Tesla Inc.", "ytdReturn": 45.67, "monthlyReturns": [{"x": "Jan", "y": 8.5}, {"x": "Feb", "y": -5.2}, {"x": "Mar", "y": 6.3}, {"x": "Apr", "y": 3.7}, {"x": "May", "y": -2.8}, {"x": "Jun", "y": 7.9}, {"x": "Jul", "y": 4.2}, {"x": "Aug", "y": -6.1}, {"x": "Sep", "y": 9.2}, {"x": "Oct", "y": 5.3}, {"x": "Nov", "y": 6.7}, {"x": "Dec", "y": 3.2}], "bestMonth": 9.2},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "ytdReturn": 87.23, "monthlyReturns": [{"x": "Jan", "y": 12.3}, {"x": "Feb", "y": -6.8}, {"x": "Mar", "y": 9.4}, {"x": "Apr", "y": 7.2}, {"x": "May", "y": -3.9}, {"x": "Jun", "y": 11.6}, {"x": "Jul", "y": 8.1}, {"x": "Aug", "y": -9.2}, {"x": "Sep", "y": 13.7}, {"x": "Oct", "y": 9.8}, {"x": "Nov", "y": 11.2}, {"x": "Dec", "y": 7.9}], "bestMonth": 13.7},
    ]


@register_widget({
    "name": "Table Widget with Custom Formatter",
    "description": "A table widget with custom sparkline formatter for profit/loss",
    "type": "table",
    "endpoint": "table_widget_custom_formatter",
    "gridData": {"w": 20, "h": 6},
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "company", "headerName": "Company", "cellDataType": "text", "width": 150, "pinned": "left"},
                {
                    "field": "profit_loss",
                    "headerName": "P&L Trend",
                    "width": 200,
                    "sparkline": {
                        "type": "bar",
                        "options": {
                            "customFormatter": "(params) => ({ fill: params.yValue >= 0 ? '#22c55e' : '#ef4444', stroke: params.yValue >= 0 ? '#16a34a' : '#dc2626' })"
                        },
                    },
                },
                {
                    "field": "revenue_growth",
                    "headerName": "Revenue Growth",
                    "width": 200,
                    "sparkline": {
                        "type": "bar",
                        "options": {
                            "customFormatter": "(params) => ({ fill: params.yValue > 10 ? '#22c55e' : params.yValue < 0 ? '#ef4444' : '#f59e0b', fillOpacity: 0.3, stroke: params.yValue > 10 ? '#16a34a' : params.yValue < 0 ? '#dc2626' : '#d97706' })"
                        },
                    },
                },
            ]
        }
    },
})
@router.get("/table_widget_custom_formatter")
def table_widget_custom_formatter():
    """Returns mock data with custom formatter"""
    return [
        {"company": "TechCorp", "profit_loss": [5, -2, 8, -3, 12, 7, -1], "revenue_growth": [15, 8, -5, 20, -8, 25, 18]},
        {"company": "DataSoft", "profit_loss": [10, -5, 15, -8, 20, 12, -3], "revenue_growth": [12, 5, 8, -2, 15, 10, 22]},
        {"company": "CloudInc", "profit_loss": [8, -15, 25, 12, -5, 18, 28], "revenue_growth": [8, -3, 12, 18, 6, 14, 9]},
    ]
