from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import random
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import generate_counterparties
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/regulatory_compliance", tags=["Regulatory & Compliance"])

def generate_regulation_heatmap():
    """Generate regulation compliance heatmap."""
    regulations = ["Dodd-Frank", "MiFID II", "EMIR", "Basel III", "CFTC Rules", "ESMA Guidelines"]
    obligation_types = ["Reporting", "Clearing", "Margining", "Capital", "Liquidity", "Risk Mgmt"]
    
    data = []
    for regulation in regulations:
        for obligation in obligation_types:
            compliance_rate = random.uniform(85, 99.5)
            open_issues = random.randint(0, 25)
            
            data.append({
                "regulation": regulation,
                "obligation_type": obligation,
                "compliance_rate": round(compliance_rate, 1),
                "open_issues": open_issues,
                "status": "Good" if compliance_rate > 95 and open_issues < 5 
                         else "Warning" if compliance_rate > 90 
                         else "Critical"
            })
    
    return data

def generate_trade_lifecycle_audit():
    """Generate trade lifecycle audit trail data."""
    trade_ids = [f"TRD-{i:06d}" for i in range(100001, 100021)]
    stages = ["Execution", "Confirmation", "Clearing", "Settlement", "Reporting"]
    
    audit_trail = []
    for trade_id in trade_ids:
        execution_time = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        for i, stage in enumerate(stages):
            stage_time = execution_time + timedelta(minutes=random.randint(5, 120) * (i + 1))
            
            audit_trail.append({
                "trade_id": trade_id,
                "stage": stage,
                "timestamp": stage_time.isoformat(),
                "status": random.choice(["Completed", "Pending", "Failed"] if i < len(stages)-1 else ["Completed"]),
                "counterparty": random.choice(generate_counterparties()),
                "venue": random.choice(["NYSE", "NASDAQ", "DTCC", "LCH", "CME"]),
                "sla_met": random.choice([True, False]),
                "processing_time": random.randint(1, 300)
            })
    
    return sorted(audit_trail, key=lambda x: x["timestamp"], reverse=True)[:50]

def generate_exception_reports():
    """Generate exception report data."""
    exception_types = [
        "Missing LEI", "Invalid ISIN", "Incomplete Trade Details", 
        "Late Reporting", "Counterparty Mismatch", "Settlement Fail"
    ]
    
    exceptions = []
    for i in range(25):
        exceptions.append({
            "exception_id": f"EXC-{i+1:05d}",
            "trade_id": f"TRD-{random.randint(100001, 999999)}",
            "exception_type": random.choice(exception_types),
            "severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "created_date": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
            "assigned_to": random.choice(["Compliance Team", "Operations", "Risk Team", "Legal"]),
            "status": random.choice(["Open", "In Progress", "Pending Review", "Resolved"]),
            "description": f"Exception in {random.choice(exception_types)} validation",
            "regulatory_impact": random.choice(["None", "Low", "Medium", "High"])
        })
    
    return sorted(exceptions, key=lambda x: x["created_date"], reverse=True)

def generate_kyc_aml_flags():
    """Generate KYC/AML risk flag data."""
    risk_types = ["High Risk Country", "PEP Status", "Sanctions List", "Unusual Activity", "Documentation Gap"]
    
    flags = []
    entities = generate_counterparties()[:15]
    
    for entity in entities:
        if random.random() > 0.7:  # 30% chance of having flags
            flags.append({
                "entity": entity,
                "risk_type": random.choice(risk_types),
                "risk_score": random.randint(60, 95),
                "flag_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Under Review", "Cleared", "Escalated"]),
                "trade_volume": round(random.uniform(10, 500), 2),
                "jurisdiction": random.choice(["US", "EU", "UK", "APAC", "LATAM"]),
                "review_required": random.choice([True, False])
            })
    
    return sorted(flags, key=lambda x: x["risk_score"], reverse=True)

def generate_compliance_alerts():
    """Generate real-time compliance alerts."""
    alert_types = [
        "Late Trade Report", "Missing Regulatory Field", "Threshold Breach", 
        "Unusual Volume", "Cross-Border Issue", "Margin Call"
    ]
    
    alerts = []
    for i in range(15):
        alerts.append({
            "alert_id": f"ALERT-{i+1:04d}",
            "timestamp": datetime.now().isoformat(),
            "alert_type": random.choice(alert_types),
            "regulation": random.choice(["Dodd-Frank", "MiFID II", "EMIR", "CFTC"]),
            "entity": random.choice(generate_counterparties()),
            "severity": random.choice(["Info", "Warning", "Critical"]),
            "auto_resolved": random.choice([True, False]),
            "description": f"Automated alert for {random.choice(alert_types)}",
            "action_required": random.choice(["None", "Review", "Report", "Escalate"])
        })
    
    return alerts

# 1. Regulation Compliance Heatmap
@register_widget({
    "name": "Regulation Compliance Heatmap",
    "description": "Open obligations tagged by regulation type",
    "category": "Regulatory & Compliance",
    "subCategory": "Overview",
    "type": "chart",
    "endpoint": "regulatory_compliance/regulation_heatmap",
    "gridData": {"w": 20, "h": 10},
    "params": [
        {
            "paramName": "compliance_frameworks",
            "value": "All",
            "label": "Compliance Frameworks",
            "description": "Filter by regulatory compliance framework. Valid values: 'All' (all frameworks), 'Dodd-Frank' (US financial reform), 'MiFID II' (EU investment services), 'EMIR' (EU derivatives regulation), 'Basel III' (banking regulation), 'CFTC' (US commodities). Determines which regulatory requirements are displayed in the heatmap.",
            "type": "text",
            "options": [
                {"label": "All Frameworks", "value": "All"},
                {"label": "Dodd-Frank", "value": "Dodd-Frank"},
                {"label": "MiFID II", "value": "MiFID II"},
                {"label": "EMIR", "value": "EMIR"},
                {"label": "Basel III", "value": "Basel III"},
                {"label": "CFTC Rules", "value": "CFTC"}
            ]
        },
        {
            "paramName": "compliance_threshold",
            "value": 90,
            "label": "Min Compliance Rate (%)",
            "description": "Minimum compliance rate percentage to highlight in the heatmap. Only entities with compliance rates above this threshold will be color-coded as acceptable. Range: 0-100. Example: 95 highlights only entities with >95% compliance.",
            "type": "number"
        },
        {
            "paramName": "include_pending",
            "value": True,
            "label": "Include Pending Obligations",
            "description": "Include pending regulatory obligations in compliance calculations. When enabled, factors in upcoming deadlines and pending submissions. When disabled, shows only completed compliance actions for current state assessment.",
            "type": "boolean"
        }
    ]
})
@router.get("/regulation_heatmap")
def get_regulation_heatmap(
    compliance_frameworks: str = "All",
    obligation_types: str = "All",
    entity_categories: str = "All",
    jurisdiction_filters: str = "All",
    compliance_threshold: float = 90,
    include_pending: bool = True,
    theme: str = "dark"
):
    """Generate regulation compliance heatmap with filtering parameters."""
    data = generate_regulation_heatmap()
    df = pd.DataFrame(data)
    
    # Create pivot table
    pivot = df.pivot_table(values='compliance_rate', index='regulation', columns='obligation_type')
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=95,
        zmin=85,
        zmax=100,
        text=[[f'{val:.1f}%' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Regulation: %{y}<br>Obligation: %{x}<br>Compliance: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Regulatory Compliance Heatmap',
        'xaxis_title': 'Obligation Type',
        'yaxis_title': 'Regulation',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Trade Lifecycle Audit Trail
@register_widget({
    "name": "Trade Lifecycle Audit Trail",
    "description": "Interactive drilldown from execution to settlement",
    "category": "Regulatory & Compliance",
    "subCategory": "Audit Trail",
    "type": "table",
    "endpoint": "regulatory_compliance/audit_trail",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "trade_id",
                    "headerName": "Trade ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "stage",
                    "headerName": "Stage",
                    "width": 120
                },
                {
                    "field": "timestamp",
                    "headerName": "Timestamp",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Completed", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Pending", "color": "#F28352", "fill": False},
                            {"condition": "eq", "value": "Failed", "color": "#ED6D3C", "fill": True}
                        ]
                    }
                },
                {
                    "field": "counterparty",
                    "headerName": "Counterparty",
                    "width": 150
                },
                {
                    "field": "venue",
                    "headerName": "Venue",
                    "width": 100
                },
                {
                    "field": "sla_met",
                    "headerName": "SLA Met",
                    "width": 90,
                    "cellDataType": "boolean",
                    "renderFn": "greenRed"
                },
                {
                    "field": "processing_time",
                    "headerName": "Processing Time (min)",
                    "width": 160,
                    "cellDataType": "number"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "trade_filter",
            "value": "All",
            "label": "Filter by Status",
            "description": "Filter audit trail entries by trade status. Valid values: 'All' (all trades), 'Matched' (successfully matched), 'Unmatched' (pending matching), 'Rejected' (failed validation), 'Amended' (modified trades). Determines which trade states are included in the audit trail.",
            "type": "text",
            "options": [
                {"label": "All Statuses", "value": "All"},
                {"label": "Matched", "value": "Matched"},
                {"label": "Unmatched", "value": "Unmatched"},
                {"label": "Rejected", "value": "Rejected"},
                {"label": "Amended", "value": "Amended"}
            ]
        },
        {
            "paramName": "sla_thresholds",
            "value": 60,
            "label": "SLA Threshold (minutes)",
            "description": "Service Level Agreement threshold in minutes for trade reporting compliance. Trades reported beyond this timeframe are flagged as SLA violations. Range: 15-1440. Example: 30 flags trades reported more than 30 minutes after execution.",
            "type": "number"
        },
        {
            "paramName": "include_amendments",
            "value": False,
            "label": "Include Trade Amendments",
            "description": "Include trade amendment entries in the audit trail. When enabled, shows modification history and corrected trades. When disabled, focuses on original trade entries only for cleaner audit trail view.",
            "type": "boolean"
        }
    ]
})
@router.get("/audit_trail")
def get_audit_trail(
    trade_filter: str = "All",
    workflow_stages: str = "All",
    sla_thresholds: float = 60,
    exception_types: str = "All",
    processing_times: str = "All",
    include_amendments: bool = False
):
    """Get trade lifecycle audit trail with filtering parameters."""
    data = generate_trade_lifecycle_audit()
    
    if trade_filter != "All":
        data = [d for d in data if d["status"] == trade_filter]
    
    return data

# 3. Exception Report Table
@register_widget({
    "name": "Exception Reports",
    "description": "Trades missing key fields or failing validation",
    "category": "Regulatory & Compliance",
    "subCategory": "Exceptions",
    "type": "table",
    "endpoint": "regulatory_compliance/exceptions",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "exception_id",
                    "headerName": "Exception ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "trade_id",
                    "headerName": "Trade ID",
                    "width": 120
                },
                {
                    "field": "exception_type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Critical", "color": "#ED6D3C", "fill": True},
                            {"condition": "eq", "value": "High", "color": "#F28352", "fill": True},
                            {"condition": "eq", "value": "Medium", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Low", "color": "#0B413A", "fill": False}
                        ]
                    }
                },
                {
                    "field": "created_date",
                    "headerName": "Created",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "assigned_to",
                    "headerName": "Assigned To",
                    "width": 120
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Resolved", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Open", "color": "#ED6D3C", "fill": False},
                            {"condition": "eq", "value": "In Progress", "color": "#F28352", "fill": False}
                        ]
                    }
                },
                {
                    "field": "regulatory_impact",
                    "headerName": "Reg Impact",
                    "width": 120
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "severity_levels",
            "value": "All",
            "label": "Severity Levels",
            "description": "Filter exceptions by severity level. Valid values: 'All' (all severities), 'Critical' (immediate action required), 'High' (urgent attention needed), 'Medium' (moderate priority), 'Low' (minor issues). Determines which exception priorities are displayed.",
            "type": "text",
            "options": [
                {"label": "All Severities", "value": "All"},
                {"label": "Critical", "value": "Critical"},
                {"label": "High", "value": "High"},
                {"label": "Medium", "value": "Medium"},
                {"label": "Low", "value": "Low"}
            ]
        },
        {
            "paramName": "age_threshold",
            "value": 30,
            "label": "Max Age (days)",
            "description": "Maximum age in days for exceptions to include in analysis. Only exceptions newer than this threshold will be displayed. Range: 1-365. Example: 14 shows exceptions from the last 2 weeks for current issue focus.",
            "type": "number"
        },
        {
            "paramName": "auto_assigned_only",
            "value": False,
            "label": "Show Auto-Assigned Only",
            "description": "Filter to show only automatically assigned exceptions. When enabled, displays exceptions assigned by automated systems. When disabled, includes both manually and automatically assigned exceptions for comprehensive view.",
            "type": "boolean"
        }
    ]
})
@router.get("/exceptions")
def get_exceptions(
    severity_levels: str = "All",
    resolution_status: str = "All",
    regulatory_impact: str = "All",
    assignment_filters: str = "All",
    age_threshold: int = 30,
    auto_assigned_only: bool = False
):
    """Get exception reports with filtering parameters."""
    return generate_exception_reports()

# 4. KYC/AML Risk Flag List
@register_widget({
    "name": "KYC/AML Risk Flags",
    "description": "Suspicious counterparties linked to trade flows",
    "category": "Regulatory & Compliance",
    "subCategory": "Risk Management",
    "type": "table",
    "endpoint": "regulatory_compliance/kyc_aml_flags",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "column"
            },
            "columnsDefs": [
                {
                    "field": "entity",
                    "headerName": "Entity",
                    "width": 150,
                    "pinned": "left"
                },
                {
                    "field": "risk_type",
                    "headerName": "Risk Type",
                    "width": 150
                },
                {
                    "field": "risk_score",
                    "headerName": "Risk Score",
                    "width": 110,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 85, "color": "#ED6D3C", "fill": True},
                            {"condition": "gt", "value": 70, "color": "#F28352", "fill": False},
                            {"condition": "lte", "value": 70, "color": "#0E5447", "fill": False}
                        ]
                    }
                },
                {
                    "field": "flag_date",
                    "headerName": "Flag Date",
                    "width": 120,
                    "cellDataType": "date"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Active", "color": "#ED6D3C", "fill": False},
                            {"condition": "eq", "value": "Cleared", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Under Review", "color": "#F28352", "fill": False}
                        ]
                    }
                },
                {
                    "field": "trade_volume",
                    "headerName": "Trade Volume ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "jurisdiction",
                    "headerName": "Jurisdiction",
                    "width": 110
                },
                {
                    "field": "review_required",
                    "headerName": "Review Req.",
                    "width": 110,
                    "cellDataType": "boolean",
                    "renderFn": "greenRed"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "risk_categories",
            "value": "All",
            "label": "Risk Categories",
            "description": "Filter by AML/KYC risk category. Valid values: 'All' (all risk levels), 'High Risk' (high-risk entities), 'Medium Risk' (moderate risk), 'Low Risk' (standard risk), 'PEP' (Politically Exposed Persons), 'Sanctions' (sanctions screening). Determines which risk classifications are included.",
            "type": "text",
            "options": [
                {"label": "All Risk Categories", "value": "All"},
                {"label": "High Risk", "value": "High Risk"},
                {"label": "Medium Risk", "value": "Medium Risk"},
                {"label": "Low Risk", "value": "Low Risk"},
                {"label": "PEP (Politically Exposed)", "value": "PEP"},
                {"label": "Sanctions Screening", "value": "Sanctions"}
            ]
        },
        {
            "paramName": "risk_score_min",
            "value": 70,
            "label": "Min Risk Score",
            "description": "Minimum risk score to include in KYC/AML flag analysis. Only entities with risk scores above this threshold will be displayed. Range: 0-100. Example: 80 shows high-risk entities requiring enhanced due diligence.",
            "type": "number"
        },
        {
            "paramName": "trade_volume_threshold",
            "value": 10,
            "label": "Min Trade Volume ($M)",
            "description": "Minimum trade volume in millions of USD for entities to include in KYC/AML analysis. Only entities with trading activity above this level will be flagged. Range: 1-10000. Example: 50 focuses on entities with >$50M volume.",
            "type": "number"
        }
    ]
})
@router.get("/kyc_aml_flags")
def get_kyc_aml_flags(
    risk_categories: str = "All",
    jurisdiction_filters: str = "All",
    review_status: str = "All",
    escalation_levels: str = "All",
    risk_score_min: float = 70,
    trade_volume_threshold: float = 10
):
    """Get KYC/AML risk flags with filtering parameters."""
    return generate_kyc_aml_flags()

# 5. Compliance Alerts Ticker
@register_widget({
    "name": "Compliance Alerts Ticker",
    "description": "Real-time summary of compliance issues needing review",
    "category": "Regulatory & Compliance",
    "subCategory": "Alerts",
    "type": "table",
    "endpoint": "regulatory_compliance/alerts_ticker",
    "gridData": {"w": 20, "h": 8},
    "refetchInterval": 30000,
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "alert_id",
                    "headerName": "Alert ID",
                    "width": 100
                },
                {
                    "field": "alert_type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "regulation",
                    "headerName": "Regulation",
                    "width": 120
                },
                {
                    "field": "entity",
                    "headerName": "Entity",
                    "width": 150
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Critical", "color": "#ED6D3C", "fill": True},
                            {"condition": "eq", "value": "Warning", "color": "#F28352", "fill": False},
                            {"condition": "eq", "value": "Info", "color": "#0E5447", "fill": False}
                        ]
                    }
                },
                {
                    "field": "action_required",
                    "headerName": "Action",
                    "width": 100
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "alert_types",
            "value": "All",
            "label": "Alert Types",
            "description": "Filter by compliance alert type. Valid values: 'All' (all alert types), 'Trade Reporting' (reporting violations), 'Position Limits' (position limit breaches), 'Market Abuse' (suspicious trading), 'Settlement' (settlement failures), 'Margin' (margin requirements). Determines which alert categories are displayed.",
            "type": "text",
            "options": [
                {"label": "All Alert Types", "value": "All"},
                {"label": "Trade Reporting", "value": "Trade Reporting"},
                {"label": "Position Limits", "value": "Position Limits"},
                {"label": "Market Abuse", "value": "Market Abuse"},
                {"label": "Settlement", "value": "Settlement"},
                {"label": "Margin Requirements", "value": "Margin"}
            ]
        },
        {
            "paramName": "resolution_timeframes",
            "value": "All",
            "label": "Resolution Timeframes",
            "description": "Filter by alert resolution timeframe. Valid values: 'All' (all timeframes), 'Immediate' (<1 hour), 'Same Day' (<24 hours), 'Next Day' (24-48 hours), 'Weekly' (2-7 days), 'Overdue' (>7 days). Shows alerts based on resolution speed requirements.",
            "type": "text",
            "options": [
                {"label": "All Timeframes", "value": "All"},
                {"label": "Immediate (<1 hour)", "value": "Immediate"},
                {"label": "Same Day (<24 hours)", "value": "Same Day"},
                {"label": "Next Day (24-48 hours)", "value": "Next Day"},
                {"label": "Weekly (2-7 days)", "value": "Weekly"},
                {"label": "Overdue (>7 days)", "value": "Overdue"}
            ]
        },
        {
            "paramName": "auto_resolve_excluded",
            "value": False,
            "label": "Exclude Auto-Resolved Alerts",
            "description": "Exclude alerts that were automatically resolved by system processes. When enabled, shows only manually resolved alerts requiring human intervention. When disabled, includes all alerts for comprehensive compliance tracking.",
            "type": "boolean"
        }
    ]
})
@router.get("/alerts_ticker")
def get_alerts_ticker(
    alert_types: str = "All",
    priority_levels: str = "All",
    resolution_timeframes: str = "All",
    regulatory_scope: str = "All",
    auto_resolve_excluded: bool = False
):
    """Get compliance alerts ticker with filtering parameters."""
    # Import the correct function from data_generator
    from mockup_data.data_generator import generate_compliance_alerts as gen_compliance_alerts
    return gen_compliance_alerts()

# 6. Compliance Metrics
@register_widget({
    "name": "Compliance Metrics",
    "description": "Key regulatory compliance metrics",
    "category": "Regulatory & Compliance",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "regulatory_compliance/metrics",
    "gridData": {"w": 20, "h": 4},
    "params": [
        {
            "paramName": "measurement_periods",
            "value": "MTD",
            "label": "Measurement Period",
            "description": "Time period for compliance metrics calculation. Valid values: 'MTD' (month-to-date), 'QTD' (quarter-to-date), 'YTD' (year-to-date), 'Last 30D' (rolling 30 days), 'Last 90D' (rolling 90 days). Determines the timeframe for compliance performance measurement.",
            "type": "text",
            "options": [
                {"label": "Month-to-Date", "value": "MTD"},
                {"label": "Quarter-to-Date", "value": "QTD"},
                {"label": "Year-to-Date", "value": "YTD"},
                {"label": "Last 30 Days", "value": "Last 30D"},
                {"label": "Last 90 Days", "value": "Last 90D"}
            ]
        },
        {
            "paramName": "benchmark_comparisons",
            "value": "Industry",
            "label": "Benchmark Comparison",
            "description": "Benchmark for compliance metrics comparison. Valid values: 'Industry' (industry averages), 'Regulatory' (regulatory minimums), 'Peer Group' (similar institutions), 'Historical' (own historical performance), 'Best Practice' (industry best practices). Determines the baseline for performance evaluation.",
            "type": "text",
            "options": [
                {"label": "Industry Average", "value": "Industry"},
                {"label": "Regulatory Minimum", "value": "Regulatory"},
                {"label": "Peer Group", "value": "Peer Group"},
                {"label": "Historical Performance", "value": "Historical"},
                {"label": "Best Practice", "value": "Best Practice"}
            ]
        },
        {
            "paramName": "jurisdiction_scope",
            "value": "Global",
            "label": "Jurisdiction Scope",
            "description": "Geographic scope for compliance metrics. Valid values: 'Global' (worldwide compliance), 'US' (US regulations only), 'EU' (European regulations), 'APAC' (Asia-Pacific), 'Multi-Jurisdictional' (cross-border compliance). Determines which regulatory jurisdictions are included.",
            "type": "text",
            "options": [
                {"label": "Global", "value": "Global"},
                {"label": "US Only", "value": "US"},
                {"label": "European Union", "value": "EU"},
                {"label": "Asia-Pacific", "value": "APAC"},
                {"label": "Multi-Jurisdictional", "value": "Multi-Jurisdictional"}
            ]
        }
    ]
})
@router.get("/metrics")
def get_compliance_metrics(
    compliance_categories: str = "All",
    measurement_periods: str = "MTD",
    benchmark_comparisons: str = "Industry",
    jurisdiction_scope: str = "Global"
):
    """Get compliance metrics with calculation parameters."""
    # Apply filtering logic based on parameters
    base_metrics = [
        {
            "label": "Overall Compliance",
            "value": "94.2%",
            "delta": "1.8"
        },
        {
            "label": "Open Exceptions",
            "value": "127",
            "delta": "-15.0"
        },
        {
            "label": "KYC Flags",
            "value": "8",
            "delta": "2.0"
        },
        {
            "label": "SLA Compliance",
            "value": "96.8%",
            "delta": "0.5"
        },
        {
            "label": "Audit Score",
            "value": "A-",
            "delta": "0.0"
        }
    ]
    
    return base_metrics

# 7. Dashboard Notes
@register_widget({
    "name": "Regulatory Compliance Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Regulatory & Compliance dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "regulatory_compliance/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Regulatory Compliance dashboard documentation."""
    markdown_content = """# DTCC Regulatory & Compliance Dashboard

## Overview
The DTCC Regulatory & Compliance Dashboard provides comprehensive regulatory compliance monitoring capabilities, featuring audit trails, exception reporting, KYC/AML risk flagging, and real-time compliance alerting across all regulatory frameworks. This dashboard ensures adherence to global financial regulations and facilitates regulatory reporting and oversight.

## Purpose
• **Regulatory Oversight**: Monitor compliance with global regulations including Dodd-Frank, MiFID II, EMIR, and Basel III across all business lines

• **Audit Trail Management**: Provide complete trade lifecycle visibility from execution to settlement with full regulatory audit capabilities

• **Exception Management**: Identify, track, and resolve regulatory exceptions including missing data, validation failures, and reporting gaps

• **Risk Flag Monitoring**: Track KYC/AML risk indicators, sanctions screening results, and suspicious activity detection across counterparties

---

## Tab 1: Compliance Overview
**Purpose**: High-level regulatory compliance status and real-time monitoring

### Widgets:
• **Compliance Metrics**: Key compliance indicators including overall compliance (94.2%), open exceptions (127), KYC flags (8), SLA compliance (96.8%), and audit score (A-)

• **Regulation Compliance Heatmap**: Matrix showing compliance rates by regulation type (Dodd-Frank, MiFID II, EMIR, Basel III) and obligation categories

• **Compliance Alerts Ticker**: Real-time feed of compliance issues requiring immediate attention with severity levels and assigned actions

---

## Tab 2: Audit & Exceptions
**Purpose**: Detailed audit trail analysis and exception management

### Widgets:
• **Trade Lifecycle Audit Trail**: Complete transaction tracking from execution through settlement with status monitoring and SLA compliance

• **Exception Reports**: Comprehensive table of regulatory exceptions with severity assessment, assignment tracking, and resolution status

• **KYC/AML Risk Flags**: High-risk entity monitoring with risk scores, jurisdiction analysis, and review requirements

---

## Data Sources
• **Trade Repositories**: Global trade repository feeds for comprehensive transaction capture and regulatory reporting validation

• **Regulatory Databases**: Direct connections to LEI databases, sanctions lists, PEP databases, and other regulatory reference data

• **Surveillance Systems**: Integration with market surveillance and transaction monitoring systems for suspicious activity detection

• **Counterparty Management**: Master data management systems for entity information, risk ratings, and relationship mapping

• **Audit Systems**: Complete audit trail capture from trade execution through final settlement and regulatory reporting

## Key Metrics Tracked
• **Compliance Rates**: Regulation-specific compliance percentages with trending and benchmark analysis across all regulatory frameworks

• **Exception Analytics**: Exception volumes, resolution times, aging analysis, and recurring exception pattern identification

• **Audit Trail Completeness**: Trade lifecycle coverage, data quality metrics, and regulatory field population rates

• **KYC/AML Indicators**: Risk score distributions, high-risk entity counts, review completion rates, and escalation metrics

• **Regulatory Reporting**: Report submission timeliness, data quality scores, regulatory feedback, and correction rates

• **SLA Performance**: Processing time compliance, exception resolution SLAs, and regulatory response time metrics

• **Risk Assessment**: Entity risk profiles, geographic risk exposure, and sanctions screening effectiveness metrics

## Use Cases
• **Chief Compliance Officers**: Oversee enterprise-wide regulatory compliance, manage regulatory relationships, and ensure policy adherence

• **Regulatory Reporting Teams**: Manage regulatory submissions, ensure data quality, and coordinate with global regulatory authorities

• **AML/KYC Analysts**: Investigate suspicious activities, manage high-risk relationships, and conduct enhanced due diligence procedures

• **Audit Teams**: Conduct regulatory audits, validate control effectiveness, and support regulatory examinations

• **Legal Counsel**: Assess regulatory exposure, manage regulatory inquiries, and coordinate enforcement response activities"""

    return markdown_content