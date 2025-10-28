import random
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional, Union

def get_days_from_period(time_period: str) -> int:
    """Convert time period string to number of days."""
    period_map = {
        "1D": 1, "1W": 7, "1M": 30, "3M": 90, 
        "6M": 180, "1Y": 365, "YTD": (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    }
    return period_map.get(time_period, 30)

def generate_time_series(days=30, base_value=100, volatility=0.05, time_period: str = "1M"):
    """Generate time series data with random walk."""
    if time_period:
        days = get_days_from_period(time_period)
    
    dates = []
    values = []
    current_value = base_value
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        dates.append(date)
        
        change = random.gauss(0, volatility) * current_value
        current_value += change
        current_value = max(current_value, base_value * 0.5)
        values.append(round(current_value, 2))
    
    return dates, values

def get_all_asset_classes():
    """Get all available asset classes."""
    return [
        "Equities", "Fixed Income", "Derivatives", 
        "Commodities", "FX", "Repo", "ETFs", "Options"
    ]

def get_all_counterparty_types():
    """Get all counterparty types."""
    return ["Banks", "Asset Managers", "Hedge Funds", "Insurance", "Pension Funds", "Corporations", "Government"]

def get_all_regions():
    """Get all geographic regions."""
    return ["US", "Europe", "APAC", "Americas", "Global"]

def get_all_risk_levels():
    """Get all risk levels."""
    return ["Low", "Medium", "High", "Critical"]

def get_all_currencies():
    """Get all currencies."""
    return ["USD", "EUR", "JPY", "GBP", "CHF", "CAD", "AUD"]

def get_all_settlement_types():
    """Get all settlement types."""
    return ["T+0", "T+1", "T+2", "T+3+"]

def get_all_regulatory_frameworks():
    """Get all regulatory frameworks."""
    return ["Dodd-Frank", "MiFID II", "EMIR", "Basel III", "CFTC", "SEC", "ESMA"]

def generate_asset_classes():
    """Generate mock asset class data."""
    return get_all_asset_classes()

def generate_counterparties(counterparty_types: List[str] = None, region: str = None):
    """Generate mock counterparty data filtered by type and region."""
    all_firms = {
        "Banks": {
            "US": ["JP Morgan", "Bank of America", "Citi", "Wells Fargo", "Morgan Stanley", "Goldman Sachs"],
            "Europe": ["Deutsche Bank", "Barclays", "HSBC", "UBS", "BNP Paribas", "Societe Generale"],
            "APAC": ["Mitsubishi UFJ", "Sumitomo Mitsui", "Mizuho", "ICBC", "Bank of China"],
            "Global": ["JP Morgan", "Deutsche Bank", "Barclays", "HSBC", "Citi"]
        },
        "Asset Managers": {
            "US": ["BlackRock", "Vanguard", "Fidelity", "State Street", "BNY Mellon"],
            "Europe": ["Amundi", "Allianz", "AXA", "Legal & General", "Schroders"],
            "APAC": ["Nomura AM", "Daiwa AM", "Nikko AM", "China AMC"],
            "Global": ["BlackRock", "Vanguard", "Amundi", "State Street"]
        },
        "Hedge Funds": {
            "US": ["Bridgewater", "AQR", "Two Sigma", "Renaissance", "Citadel"],
            "Europe": ["Man Group", "Brevan Howard", "Marshall Wace", "Winton"],
            "APAC": ["Hillhouse", "Oaktree Asia", "PAG", "Boyu Capital"],
            "Global": ["Bridgewater", "Man Group", "AQR", "Citadel"]
        },
        "Insurance": {
            "US": ["Berkshire Hathaway", "AIG", "Prudential", "MetLife"],
            "Europe": ["Allianz", "AXA", "Zurich", "Munich Re", "Prudential UK"],
            "APAC": ["Ping An", "AIA", "Nippon Life", "Dai-ichi Life"],
            "Global": ["Allianz", "AXA", "Prudential", "AIG"]
        },
        "Pension Funds": {
            "US": ["CalPERS", "CalSTRS", "TIAA", "PBGC"],
            "Europe": ["ABP", "PFZW", "ATP", "USS", "BT Pension"],
            "APAC": ["GPIF", "NPS", "CPF", "KWAP"],
            "Global": ["CalPERS", "ABP", "GPIF", "ATP"]
        }
    }
    
    if not counterparty_types:
        counterparty_types = get_all_counterparty_types()
    if not region:
        region = "Global"
    
    firms = []
    for cp_type in counterparty_types:
        if cp_type in all_firms:
            region_key = region if region in all_firms[cp_type] else "Global"
            if region_key in all_firms[cp_type]:
                firms.extend(all_firms[cp_type][region_key])
    
    return list(set(firms))  # Remove duplicates

def generate_trade_volumes(time_period: str = "1D", asset_classes: List[str] = None, 
                         min_volume: float = 0, region: str = "Global", **kwargs):
    """Generate mock trade volume heatmap data with parameter filtering."""
    if not asset_classes:
        asset_classes = get_all_asset_classes()
    
    # Adjust base volume by region
    region_multiplier = {
        "US": 1.0, "Europe": 0.8, "APAC": 0.6, "Americas": 0.9, "Global": 1.2
    }
    base_multiplier = region_multiplier.get(region, 1.0)
    
    # Adjust time granularity based on period
    if time_period in ["1D"]:
        hours = [f"{i:02d}:00" for i in range(24)]
        time_key = "hour"
    elif time_period in ["1W"]:
        hours = [f"Day {i+1}" for i in range(7)]
        time_key = "day"
    else:
        days = get_days_from_period(time_period)
        hours = [f"Week {i+1}" for i in range(min(days//7, 52))]
        time_key = "week"
    
    data = []
    for asset in asset_classes:
        # Asset-specific volume patterns
        asset_multiplier = {
            "Equities": 1.2, "Fixed Income": 1.0, "Derivatives": 0.8,
            "FX": 1.5, "Commodities": 0.6, "Repo": 0.9
        }.get(asset, 1.0)
        
        for hour in hours:
            # Trading hours effect (9-16 for most markets)
            if time_key == "hour":
                hour_num = int(hour[:2])
                time_multiplier = 1.5 if 9 <= hour_num <= 16 else 0.5
            else:
                time_multiplier = random.uniform(0.8, 1.2)
            
            base_volume = random.uniform(100, 5000)
            volume = base_volume * base_multiplier * asset_multiplier * time_multiplier
            
            # Apply minimum volume filter
            if volume >= min_volume:
                data.append({
                    "asset_class": asset,
                    time_key: hour,
                    "volume": round(volume, 2),
                    "trades": random.randint(50, 500),
                    "region": region
                })
    
    return data

def generate_anomalies(severity: List[str] = None, asset_classes: List[str] = None, 
                      counterparty_types: List[str] = None, time_period: str = "3D", **kwargs):
    """Generate mock anomaly data with parameter filtering."""
    if not severity:
        severity = get_all_risk_levels()
    if not asset_classes:
        asset_classes = get_all_asset_classes()
    if not counterparty_types:
        counterparty_types = get_all_counterparty_types()
    
    anomaly_types = {
        "Settlement": ["Settlement Fail", "Settlement Delay", "Failed Delivery"],
        "Trading": ["Cancel Spike", "Price Deviation", "Volume Anomaly", "Latency Issue"],
        "Operational": ["System Outage", "Data Error", "Connectivity Issue"],
        "Compliance": ["Regulatory Breach", "Limit Violation", "Unauthorized Trade"]
    }
    
    # Flatten anomaly types
    all_anomaly_types = [item for sublist in anomaly_types.values() for item in sublist]
    
    # Generate more anomalies for longer time periods
    days = get_days_from_period(time_period)
    num_anomalies = min(max(int(days * 0.7), 5), 50)
    
    counterparties = generate_counterparties(counterparty_types)
    
    anomalies = []
    for i in range(num_anomalies):
        # Weight severity distribution (more low/medium, fewer critical)
        severity_weights = {"Low": 0.4, "Medium": 0.35, "High": 0.2, "Critical": 0.05}
        chosen_severity = random.choices(
            list(severity_weights.keys()),
            weights=list(severity_weights.values())
        )[0]
        
        if chosen_severity not in severity:
            continue
            
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, days*24))).isoformat()
        
        # Value correlates with severity
        severity_multiplier = {"Low": 1, "Medium": 3, "High": 10, "Critical": 30}
        base_value = random.uniform(100000, 1000000) * severity_multiplier[chosen_severity]
        
        anomalies.append({
            "id": f"ANO-{i+1:04d}",
            "timestamp": timestamp,
            "type": random.choice(all_anomaly_types),
            "severity": chosen_severity,
            "asset": random.choice(asset_classes),
            "counterparty": random.choice(counterparties),
            "value": round(base_value, 2),
            "status": random.choice(["Open", "Investigating", "Resolved"]),
            "region": random.choice(get_all_regions())
        })
    
    return sorted(anomalies, key=lambda x: x["timestamp"], reverse=True)

def generate_counterparty_exposures(counterparty_types: List[str] = None, 
                                   risk_levels: List[str] = None, 
                                   min_exposure: float = 0, region: str = "Global", **kwargs):
    """Generate counterparty exposure network data with parameter filtering."""
    if not counterparty_types:
        counterparty_types = get_all_counterparty_types()
    if not risk_levels:
        risk_levels = get_all_risk_levels()
    
    firms = generate_counterparties(counterparty_types, region)[:15]
    
    nodes = []
    links = []
    
    # Risk level weights for realistic distribution
    risk_weights = {"Low": (0, 30), "Medium": (30, 60), "High": (60, 85), "Critical": (85, 100)}
    
    for i, firm in enumerate(firms):
        # Exposure varies by counterparty type
        cp_type = random.choice(counterparty_types)
        type_multiplier = {
            "Banks": 5.0, "Asset Managers": 3.0, "Hedge Funds": 2.0,
            "Insurance": 4.0, "Pension Funds": 3.5, "Corporations": 1.5
        }.get(cp_type, 1.0)
        
        base_exposure = random.uniform(100, 1000) * type_multiplier
        
        # Generate risk score based on allowed risk levels
        available_risks = [(level, range_) for level, range_ in risk_weights.items() if level in risk_levels]
        if available_risks:
            chosen_risk_level, (min_risk, max_risk) = random.choice(available_risks)
            risk_score = random.uniform(min_risk, max_risk)
        else:
            risk_score = random.uniform(0, 100)
        
        exposure = base_exposure * (1 + risk_score/100)  # Higher risk = higher exposure
        
        if exposure >= min_exposure:
            nodes.append({
                "id": firm,
                "group": i % len(counterparty_types),
                "exposure": round(exposure, 2),
                "risk_score": round(risk_score, 1),
                "type": cp_type,
                "region": region
            })
    
    # Generate links between nodes
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            # Higher probability of links between same types
            same_type = nodes[i]["type"] == nodes[j]["type"]
            link_prob = 0.4 if same_type else 0.2
            
            if random.random() < link_prob:
                exposure_factor = (nodes[i]["exposure"] + nodes[j]["exposure"]) / 2000
                link_value = random.uniform(10, 500) * exposure_factor
                
                links.append({
                    "source": nodes[i]["id"],
                    "target": nodes[j]["id"],
                    "value": round(link_value, 2)
                })
    
    return {"nodes": nodes, "links": links}

def generate_compliance_alerts(regulatory_scope: List[str] = None, severity: List[str] = None,
                             entity_type: List[str] = None, time_period: str = "1W", **kwargs):
    """Generate mock compliance alerts with parameter filtering."""
    if not regulatory_scope:
        regulatory_scope = get_all_regulatory_frameworks()
    if not severity:
        severity = get_all_risk_levels()
    if not entity_type:
        entity_type = get_all_counterparty_types()
    
    alert_types = {
        "Dodd-Frank": ["Swap Reporting", "Clearing Requirement", "Margin Compliance", "Position Limits"],
        "MiFID II": ["Best Execution", "Transaction Reporting", "Market Data", "Research Unbundling"],
        "EMIR": ["Trade Reporting", "Risk Mitigation", "Clearing Obligation", "Margin Requirements"],
        "Basel III": ["Capital Adequacy", "Liquidity Coverage", "Leverage Ratio", "NSFR Compliance"],
        "CFTC": ["Position Reporting", "Block Trade", "Swap Execution", "Record Keeping"],
        "SEC": ["Disclosure", "Insider Trading", "Market Manipulation", "Registration"],
        "ESMA": ["Short Selling", "Benchmark Regulation", "CSDR", "Market Structure"]
    }
    
    days = get_days_from_period(time_period)
    num_alerts = min(max(int(days * 0.5), 3), 25)
    
    entities = generate_counterparties(entity_type)
    
    alerts = []
    for i in range(num_alerts):
        regulation = random.choice(regulatory_scope)
        alert_type_list = alert_types.get(regulation, ["General Compliance"])
        
        # Severity distribution
        severity_weights = {"Low": 0.5, "Medium": 0.3, "High": 0.15, "Critical": 0.05}
        chosen_severity = random.choices(
            [s for s in severity_weights.keys() if s in severity],
            weights=[severity_weights[s] for s in severity_weights.keys() if s in severity]
        )[0] if severity else "Medium"
        
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, days*24))).isoformat()
        
        alerts.append({
            "id": f"COMP-{i+1:04d}",
            "timestamp": timestamp,
            "type": random.choice(alert_type_list),
            "regulation": regulation,
            "entity": random.choice(entities),
            "entity_type": random.choice(entity_type),
            "severity": chosen_severity,
            "description": f"Compliance issue detected for {regulation} regulation",
            "status": random.choice(["Open", "Under Review", "Resolved", "Escalated"]),
            "region": random.choice(get_all_regions())
        })
    
    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)

def generate_treasury_volumes(time_period: str = "1M", currencies: List[str] = None, 
                             min_volume: float = 0, region: str = "US", **kwargs):
    """Generate treasury trade volume data by tenor with enhanced parameters."""
    if not currencies:
        currencies = ["USD"]  # Treasury volumes typically in USD
    
    # Treasury types vary by region
    treasury_types = {
        "US": ["Bills (1-12M)", "Notes (2-10Y)", "Bonds (20-30Y)", "TIPS", "FRNs"],
        "Europe": ["German Bunds", "French OATs", "Italian BTPs", "Spanish Bonos"],
        "APAC": ["Japanese JGBs", "Australian AGSBs", "Korean KTBs"],
        "Global": ["Bills (1-12M)", "Notes (2-10Y)", "Bonds (20-30Y)", "TIPS", "FRNs"]
    }
    
    tenors = treasury_types.get(region, treasury_types["Global"])
    days = get_days_from_period(time_period)
    dates, _ = generate_time_series(days, time_period=time_period)
    
    data = []
    for tenor in tenors:
        volumes = []
        for date in dates:
            # Different volume patterns by tenor type
            if "Bills" in tenor or "1-12M" in tenor:
                base_volume = random.uniform(100, 800)
            elif "Notes" in tenor or "2-10Y" in tenor:
                base_volume = random.uniform(80, 600)
            else:  # Bonds and others
                base_volume = random.uniform(50, 400)
            
            # Regional volume adjustments
            region_multiplier = {"US": 1.0, "Europe": 0.7, "APAC": 0.5, "Global": 1.2}
            volume = base_volume * region_multiplier.get(region, 1.0)
            
            if volume >= min_volume:
                volumes.append(round(volume, 2))
            else:
                volumes.append(0)
        
        data.append({
            "tenor": tenor,
            "dates": dates,
            "volumes": volumes,
            "currency": currencies[0],
            "region": region
        })
    
    return data

def generate_repo_rates(time_period: str = "1M", currencies: List[str] = None, 
                       region: str = "US", **kwargs):
    """Generate repo rate data with enhanced parameters."""
    if not currencies:
        currencies = ["USD"]
    
    days = get_days_from_period(time_period)
    
    # Base rates vary by region and currency
    base_rates = {
        "US": {"USD": {"GCF_Repo": 2.5, "SOFR": 2.45, "ON_RRP": 2.4}},
        "Europe": {"EUR": {"ESTR": 1.8, "ESTER": 1.75, "EUREP": 1.85}},
        "APAC": {"JPY": {"TONAR": 0.1, "TIBOR": 0.15, "REPO": 0.12}},
        "Global": {"USD": {"GCF_Repo": 2.5, "SOFR": 2.45, "ON_RRP": 2.4}}
    }
    
    result = {}
    
    for currency in currencies:
        if region in base_rates and currency in base_rates[region]:
            rates_config = base_rates[region][currency]
        else:
            # Fallback to USD rates
            rates_config = base_rates["Global"]["USD"]
        
        dates, _ = generate_time_series(days, time_period=time_period)
        result["dates"] = dates
        
        for rate_name, base_value in rates_config.items():
            _, rates = generate_time_series(days, base_value=base_value, 
                                          volatility=0.01, time_period=time_period)
            result[f"{rate_name}_{currency}"] = rates
    
    return result

def generate_settlement_fails(settlement_types: List[str] = None, 
                             asset_classes: List[str] = None,
                             min_amount: float = 0, region: str = "US", **kwargs):
    """Generate settlement fails data with enhanced parameters."""
    if not settlement_types:
        settlement_types = get_all_settlement_types()
    if not asset_classes:
        asset_classes = ["Fixed Income"]  # Settlement fails typically in bonds
    
    # Generate more realistic security identifiers by region
    securities = {
        "US": [f"CUSIP{i:04d}" for i in range(1, 21)],
        "Europe": [f"ISIN{i:06d}" for i in range(1, 21)],
        "APAC": [f"SEDOL{i:05d}" for i in range(1, 21)],
        "Global": [f"CUSIP{i:04d}" for i in range(1, 21)]
    }
    
    cusips = securities.get(region, securities["Global"])
    tenors = ["2Y", "5Y", "10Y", "30Y"]
    
    data = []
    for cusip in cusips:
        for settle_type in settlement_types:
            # Fail rates vary by settlement type
            settle_multiplier = {"T+0": 0.1, "T+1": 0.3, "T+2": 1.0, "T+3+": 2.0}
            base_fail_rate = random.uniform(0, 5) * settle_multiplier.get(settle_type, 1.0)
            
            # Fail amounts vary by asset class
            asset_multiplier = {
                "Fixed Income": 1.0, "Equities": 0.7, "Derivatives": 0.5,
                "Repo": 1.2, "FX": 0.3
            }
            
            asset_class = random.choice(asset_classes)
            base_amount = random.uniform(0, 100) * 1000000 * asset_multiplier.get(asset_class, 1.0)
            
            if base_amount >= min_amount:
                data.append({
                    "security_id": cusip,
                    "asset_class": asset_class,
                    "tenor": random.choice(tenors),
                    "settlement_type": settle_type,
                    "fails_amount": round(base_amount, 2),
                    "fail_rate": round(base_fail_rate, 2),
                    "days_failed": random.randint(0, 10),
                    "counterparty": random.choice(generate_counterparties(region=region)[:10]),
                    "region": region
                })
    
    return sorted(data, key=lambda x: x["fails_amount"], reverse=True)

def generate_dealer_activity(counterparty_types: List[str] = None, 
                            min_volume: float = 0, region: str = "Global",
                            time_period: str = "1M", **kwargs):
    """Generate dealer activity leaderboard with enhanced parameters."""
    if not counterparty_types:
        counterparty_types = ["Banks"]  # Dealers are typically banks
    
    dealers = generate_counterparties(counterparty_types, region)[:15]
    
    # Volume scales with time period
    days = get_days_from_period(time_period)
    time_multiplier = days / 30  # Scale relative to 1 month baseline
    
    data = []
    for dealer in dealers:
        lending_vol = random.uniform(100, 2000) * time_multiplier
        borrowing_vol = random.uniform(100, 2000) * time_multiplier
        total_vol = lending_vol + borrowing_vol
        
        if total_vol >= min_volume:
            data.append({
                "dealer": dealer,
                "lending_volume": round(lending_vol, 2),
                "borrowing_volume": round(borrowing_vol, 2),
                "net_position": round(lending_vol - borrowing_vol, 2),
                "market_share": round(random.uniform(1, 15), 1),
                "region": region,
                "time_period": time_period
            })
    
    return sorted(data, key=lambda x: x["lending_volume"] + x["borrowing_volume"], reverse=True)

def generate_swap_notionals(currencies: List[str] = None, time_period: str = "1M",
                           min_notional: float = 0, region: str = "Global", **kwargs):
    """Generate swap notional data with enhanced parameters."""
    if not currencies:
        currencies = get_all_currencies()
    
    tenors = ["1Y", "2Y", "5Y", "10Y", "30Y"]
    
    # Volume adjustments by region
    region_multiplier = {"US": 1.0, "Europe": 0.8, "APAC": 0.6, "Global": 1.2}
    multiplier = region_multiplier.get(region, 1.0)
    
    # Time period adjustments
    days = get_days_from_period(time_period)
    time_multiplier = days / 30  # Scale relative to 1 month
    
    data = []
    for currency in currencies:
        # Currency-specific volume patterns
        currency_multiplier = {
            "USD": 1.0, "EUR": 0.8, "GBP": 0.6, "JPY": 0.7,
            "CHF": 0.4, "CAD": 0.3, "AUD": 0.3
        }.get(currency, 0.5)
        
        for tenor in tenors:
            # Longer tenors typically have lower volumes
            tenor_multiplier = {
                "1Y": 1.2, "2Y": 1.0, "5Y": 0.8, "10Y": 0.6, "30Y": 0.4
            }.get(tenor, 1.0)
            
            base_notional = random.uniform(100, 5000)
            notional = base_notional * multiplier * time_multiplier * currency_multiplier * tenor_multiplier
            
            if notional >= min_notional:
                data.append({
                    "currency": currency,
                    "tenor": tenor,
                    "notional": round(notional, 2),
                    "trades": random.randint(10, 500),
                    "avg_size": round(random.uniform(1, 50), 2),
                    "region": region,
                    "time_period": time_period
                })
    
    return data

def generate_cds_spreads(time_period: str = "1M", region: str = "Global", 
                        risk_levels: List[str] = None, **kwargs):
    """Generate CDS spread data with enhanced parameters."""
    if not risk_levels:
        risk_levels = get_all_risk_levels()
    
    # Regional CDS indices
    regional_indices = {
        "US": ["CDX.IG", "CDX.HY", "CDX.EM", "LCDX"],
        "Europe": ["iTraxx Europe", "iTraxx XOver", "iTraxx SenFin", "iTraxx SubFin"],
        "APAC": ["iTraxx Asia", "iTraxx Japan", "iTraxx Australia"],
        "Global": ["CDX.IG", "CDX.HY", "iTraxx Europe", "iTraxx XOver"]
    }
    
    indices = regional_indices.get(region, regional_indices["Global"])
    
    # Risk-based single names
    risk_names = {
        "Low": ["AAPL", "MSFT", "GOOGL", "JNJ", "PG"],
        "Medium": ["JPM", "BAC", "WFC", "GS", "MS"],
        "High": ["F", "GM", "CCL", "AAL", "UAL"],
        "Critical": ["TSLA", "NFLX", "ZM", "BYND", "SPCE"]
    }
    
    single_names = []
    for risk_level in risk_levels:
        if risk_level in risk_names:
            single_names.extend(risk_names[risk_level])
    
    if not single_names:
        single_names = risk_names["Medium"]  # Fallback
    
    days = get_days_from_period(time_period)
    dates, _ = generate_time_series(days, time_period=time_period)
    
    data = {
        "indices": [],
        "single_names": []
    }
    
    # Generate index spreads
    for index in indices:
        # Spread ranges vary by index type
        if "IG" in index:  # Investment Grade
            spread_range = (30, 120)
        elif "HY" in index or "XOver" in index:  # High Yield
            spread_range = (200, 600)
        else:  # Other indices
            spread_range = (50, 300)
        
        spreads = [round(random.uniform(*spread_range), 2) for _ in dates]
        data["indices"].append({
            "name": index,
            "dates": dates,
            "spreads": spreads,
            "region": region
        })
    
    # Generate single name spreads
    for name in single_names[:10]:  # Limit to 10 names
        # Spread based on risk level
        if name in risk_names["Low"]:
            spread_range = (10, 80)
        elif name in risk_names["Medium"]:
            spread_range = (50, 200)
        elif name in risk_names["High"]:
            spread_range = (150, 500)
        else:  # Critical
            spread_range = (300, 1000)
        
        spreads = [round(random.uniform(*spread_range), 2) for _ in dates]
        data["single_names"].append({
            "name": name,
            "dates": dates,
            "spreads": spreads,
            "region": region
        })
    
    return data

def generate_etf_flows(asset_classes: List[str] = None, time_period: str = "1W",
                      min_flow: float = 0, region: str = "US", **kwargs):
    """Generate ETF creation/redemption flow data with enhanced parameters."""
    if not asset_classes:
        asset_classes = ["Equities", "Fixed Income"]
    
    # ETFs by asset class and region
    etf_mapping = {
        "US": {
            "Equities": ["SPY", "QQQ", "IWM", "VTI", "VOO"],
            "Fixed Income": ["TLT", "IEF", "LQD", "HYG", "AGG"],
            "Commodities": ["GLD", "SLV", "USO", "DBA", "PDBC"],
            "FX": ["UUP", "FXE", "FXY", "UDN"],
            "Derivatives": ["VIX", "UVXY", "VIXY"]
        },
        "Europe": {
            "Equities": ["EWG", "EWU", "EWP", "EWI", "EWQ"],
            "Fixed Income": ["BUND", "GILT", "OAT"],
            "Commodities": ["PHAU", "PSLV"]
        },
        "APAC": {
            "Equities": ["EWJ", "FXI", "EWY", "EWT", "EWA"],
            "Fixed Income": ["JGBD", "CHIB"]
        },
        "Global": {
            "Equities": ["VT", "ACWI", "EEM", "VEA", "VWO"],
            "Fixed Income": ["BNDX", "VGIT", "IGOV"]
        }
    }
    
    # Get relevant ETFs
    etfs = []
    region_etfs = etf_mapping.get(region, etf_mapping["Global"])
    for asset_class in asset_classes:
        if asset_class in region_etfs:
            etfs.extend(region_etfs[asset_class])
    
    if not etfs:
        etfs = ["SPY", "QQQ", "TLT"]  # Fallback
    
    days = get_days_from_period(time_period)
    dates, _ = generate_time_series(days, time_period=time_period)
    
    data = []
    for etf in etfs[:8]:  # Limit to 8 ETFs
        for date in dates:
            # Flow magnitude varies by asset class
            if etf in etf_mapping.get("US", {}).get("Equities", []):
                flow_scale = 1.0
            elif etf in etf_mapping.get("US", {}).get("Fixed Income", []):
                flow_scale = 0.8
            elif etf in etf_mapping.get("US", {}).get("Commodities", []):
                flow_scale = 0.6
            else:
                flow_scale = 0.7
            
            creation = round(random.uniform(0, 500) * flow_scale, 2)
            redemption = round(random.uniform(0, 500) * flow_scale, 2)
            net_flow = round(creation - redemption, 2)
            
            if abs(net_flow) >= min_flow:
                data.append({
                    "etf": etf,
                    "date": date,
                    "creation": creation,
                    "redemption": redemption,
                    "net_flow": net_flow,
                    "region": region,
                    "asset_class": next((ac for ac in asset_classes 
                                       if etf in etf_mapping.get(region, {}).get(ac, [])), "Unknown")
                })
    
    return data

def generate_short_interest(asset_classes: List[str] = None, region: str = "US",
                          min_shares: int = 0, risk_levels: List[str] = None, **kwargs):
    """Generate short interest data with enhanced parameters."""
    if not asset_classes:
        asset_classes = ["Equities"]
    if not risk_levels:
        risk_levels = get_all_risk_levels()
    
    # Symbols by region and risk level
    symbols_by_region = {
        "US": {
            "Low": ["AAPL", "MSFT", "GOOGL", "JNJ", "PG", "KO", "WMT"],
            "Medium": ["AMZN", "META", "NVDA", "NFLX", "CRM", "ADBE"],
            "High": ["TSLA", "AMD", "SQ", "ROKU", "PTON", "ZM"],
            "Critical": ["GME", "AMC", "MVIS", "CLOV", "WISH"]
        },
        "Europe": {
            "Low": ["ASML", "SAP", "LVMH", "NESN", "ROG"],
            "Medium": ["RDSA", "AZN", "TM", "UL", "BAS"],
            "High": ["VOW3", "BMW", "SIE", "ALV", "DTE"]
        },
        "APAC": {
            "Low": ["TSM", "BABA", "TCEHY", "TM", "SONY"],
            "Medium": ["JD", "BIDU", "NIO", "XPEV", "LI"],
            "High": ["DIDI", "TME", "BILI", "FUTU"]
        }
    }
    
    # Get symbols based on region and risk levels
    symbols = []
    region_symbols = symbols_by_region.get(region, symbols_by_region["US"])
    for risk_level in risk_levels:
        if risk_level in region_symbols:
            symbols.extend(region_symbols[risk_level])
    
    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Fallback
    
    data = []
    for symbol in symbols[:15]:  # Limit to 15 symbols
        # Short interest varies by risk level
        if symbol in region_symbols.get("Low", []):
            short_multiplier = random.uniform(0.5, 2.0)
            borrow_rate_range = (0.5, 3.0)
        elif symbol in region_symbols.get("Medium", []):
            short_multiplier = random.uniform(1.0, 5.0)
            borrow_rate_range = (1.0, 8.0)
        elif symbol in region_symbols.get("High", []):
            short_multiplier = random.uniform(3.0, 15.0)
            borrow_rate_range = (5.0, 25.0)
        else:  # Critical
            short_multiplier = random.uniform(10.0, 50.0)
            borrow_rate_range = (15.0, 100.0)
        
        shares_short = round(random.uniform(1, 20) * 1000000 * short_multiplier)
        
        if shares_short >= min_shares:
            data.append({
                "symbol": symbol,
                "shares_short": shares_short,
                "short_ratio": round(random.uniform(1, 10), 2),
                "days_to_cover": round(random.uniform(1, 5), 1),
                "borrow_rate": round(random.uniform(*borrow_rate_range), 2),
                "change_7d": round(random.uniform(-20, 20), 2),
                "region": region,
                "risk_level": next((rl for rl in risk_levels 
                                   if symbol in region_symbols.get(rl, [])), "Medium")
            })
    
    return sorted(data, key=lambda x: x["shares_short"], reverse=True)

def generate_derivatives_data(asset_classes: List[str] = None, currencies: List[str] = None,
                             time_period: str = "1M", min_notional: float = 0, **kwargs):
    """Generate derivatives market data including swaps, options, and futures."""
    if not asset_classes:
        asset_classes = ["Derivatives"]
    if not currencies:
        currencies = get_all_currencies()
    
    days = get_days_from_period(time_period)
    
    # Swap Notionals
    swap_data = []
    tenors = ["1Y", "2Y", "5Y", "10Y", "30Y"]
    
    for currency in currencies:
        for tenor in tenors:
            notional = random.uniform(100, 5000)
            if notional >= min_notional:
                swap_data.append({
                    "currency": currency,
                    "tenor": tenor,
                    "notional": round(notional, 2),
                    "trades": random.randint(10, 500),
                    "avg_size": round(random.uniform(1, 50), 2),
                    "type": "Interest Rate Swap"
                })
    
    # Options Data
    options_data = []
    underlying_assets = ["SPY", "QQQ", "IWM", "GLD", "TLT", "EUR/USD", "GBP/USD"]
    
    for asset in underlying_assets:
        for expiry in ["1W", "1M", "3M", "6M"]:
            volume = random.uniform(1000, 50000)
            options_data.append({
                "underlying": asset,
                "expiry": expiry,
                "call_volume": round(volume * random.uniform(0.4, 0.7), 2),
                "put_volume": round(volume * random.uniform(0.3, 0.6), 2),
                "implied_vol": round(random.uniform(0.15, 0.45), 3),
                "open_interest": random.randint(10000, 500000)
            })
    
    # Volatility Surface
    vol_surface = []
    strikes = [0.8, 0.9, 1.0, 1.1, 1.2]  # Moneyness
    expiries = [30, 60, 90, 180, 365]  # Days to expiry
    
    for strike in strikes:
        for expiry in expiries:
            vol = 0.2 + random.uniform(-0.1, 0.1) + abs(strike - 1.0) * 0.1
            vol_surface.append({
                "strike": strike,
                "expiry": expiry,
                "implied_vol": round(max(vol, 0.05), 3)
            })
    
    return {
        "swaps": swap_data,
        "options": options_data,
        "volatility_surface": vol_surface
    }

def generate_equity_data(settlement_types: List[str] = None, currencies: List[str] = None,
                        time_period: str = "1M", region: str = "Global", **kwargs):
    """Generate equity market data including settlement timelines and flows."""
    if not settlement_types:
        settlement_types = get_all_settlement_types()
    if not currencies:
        currencies = ["USD"]
    
    days = get_days_from_period(time_period)
    
    # Settlement Timeline Data
    settlement_data = []
    trade_types = ["Block Trade", "Program Trade", "Cross Trade", "DMA Trade"]
    
    for settle_type in settlement_types:
        for trade_type in trade_types:
            # Settlement timing affects volume distribution
            timing_multiplier = {"T+0": 0.3, "T+1": 0.8, "T+2": 1.0, "T+3+": 0.4}
            base_volume = random.uniform(1000, 10000) * timing_multiplier.get(settle_type, 1.0)
            
            settlement_data.append({
                "settlement_type": settle_type,
                "trade_type": trade_type,
                "volume": round(base_volume, 2),
                "count": random.randint(100, 5000),
                "avg_value": round(random.uniform(10000, 1000000), 2),
                "region": region
            })
    
    # ETF Creation/Redemption with enhanced parameters
    etf_data = []
    etf_categories = {
        "Equity": ["SPY", "QQQ", "IWM", "VTI", "VOO"],
        "Fixed Income": ["TLT", "IEF", "LQD", "HYG", "AGG"],
        "Commodity": ["GLD", "SLV", "USO", "DBA", "PDBC"],
        "International": ["EEM", "VEA", "VWO", "IEFA", "IEMG"]
    }
    
    dates, _ = generate_time_series(days)
    
    for category, etfs in etf_categories.items():
        for etf in etfs[:3]:  # Limit to 3 per category
            for i, date in enumerate(dates[-7:]):  # Last 7 days for recent data
                creation = round(random.uniform(0, 500) * (1.2 if category == "Equity" else 0.8), 2)
                redemption = round(random.uniform(0, 500) * (1.1 if category == "Equity" else 0.9), 2)
                
                etf_data.append({
                    "etf": etf,
                    "category": category,
                    "date": date,
                    "creation": creation,
                    "redemption": redemption,
                    "net_flow": round(creation - redemption, 2),
                    "aum": round(random.uniform(1000, 50000), 2)
                })
    
    # Short Interest with enhanced filtering
    short_data = []
    sectors = ["Technology", "Healthcare", "Financial", "Energy", "Consumer", "Industrial"]
    
    for sector in sectors:
        symbols = [f"{sector[:3].upper()}{i}" for i in range(1, 6)]  # Generate sector symbols
        for symbol in symbols:
            short_data.append({
                "symbol": symbol,
                "sector": sector,
                "shares_short": round(random.uniform(1, 50) * 1000000),
                "short_ratio": round(random.uniform(1, 10), 2),
                "days_to_cover": round(random.uniform(1, 5), 1),
                "borrow_rate": round(random.uniform(0.5, 15), 2),
                "change_7d": round(random.uniform(-20, 20), 2),
                "region": region
            })
    
    return {
        "settlement_timeline": settlement_data,
        "etf_flows": etf_data,
        "short_interest": sorted(short_data, key=lambda x: x["shares_short"], reverse=True)
    }

def generate_compliance_data(regulatory_frameworks: List[str] = None, 
                           entity_types: List[str] = None,
                           time_period: str = "1M", region: str = "Global", **kwargs):
    """Generate comprehensive compliance and regulatory data."""
    if not regulatory_frameworks:
        regulatory_frameworks = get_all_regulatory_frameworks()
    if not entity_types:
        entity_types = get_all_counterparty_types()
    
    days = get_days_from_period(time_period)
    
    # Regulatory Heatmap
    heatmap_data = []
    compliance_areas = {
        "Trade Reporting": ["Accuracy", "Timeliness", "Completeness"],
        "Risk Management": ["Capital Adequacy", "Liquidity", "Operational Risk"],
        "Market Conduct": ["Best Execution", "Client Protection", "Fair Dealing"],
        "Data Quality": ["Validation", "Reconciliation", "Audit Trail"]
    }
    
    for framework in regulatory_frameworks:
        for area, metrics in compliance_areas.items():
            for metric in metrics:
                # Compliance score varies by framework complexity
                framework_complexity = {
                    "Dodd-Frank": 0.85, "MiFID II": 0.90, "EMIR": 0.88,
                    "Basel III": 0.82, "CFTC": 0.86, "SEC": 0.89, "ESMA": 0.87
                }
                base_score = framework_complexity.get(framework, 0.85)
                score = min(100, max(0, base_score * 100 + random.uniform(-15, 10)))
                
                heatmap_data.append({
                    "framework": framework,
                    "area": area,
                    "metric": metric,
                    "score": round(score, 1),
                    "status": "Pass" if score >= 80 else "Fail" if score < 60 else "Warning",
                    "region": region
                })
    
    # Audit Trail
    audit_data = []
    actions = ["Trade Execution", "Risk Calculation", "Reporting Submission", 
              "Data Validation", "Exception Handling", "Alert Generation"]
    
    for i in range(min(days * 5, 100)):  # 5 audit entries per day max
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, days*24))).isoformat()
        
        audit_data.append({
            "id": f"AUD-{i+1:06d}",
            "timestamp": timestamp,
            "action": random.choice(actions),
            "user": f"User{random.randint(1, 50)}",
            "entity": random.choice(generate_counterparties(entity_types, region)),
            "framework": random.choice(regulatory_frameworks),
            "status": random.choice(["Success", "Warning", "Error"]),
            "details": f"Automated {random.choice(actions).lower()} process"
        })
    
    # Exception Reports
    exception_data = []
    exception_types = {
        "Data Quality": ["Missing Field", "Invalid Format", "Duplicate Record"],
        "Business Rules": ["Limit Breach", "Threshold Violation", "Workflow Error"],
        "Regulatory": ["Late Reporting", "Incomplete Submission", "Format Mismatch"]
    }
    
    for category, types in exception_types.items():
        for exc_type in types:
            count = random.randint(0, 20)
            if count > 0:
                exception_data.append({
                    "category": category,
                    "type": exc_type,
                    "count": count,
                    "severity": random.choice(get_all_risk_levels()),
                    "framework": random.choice(regulatory_frameworks),
                    "resolution_time": round(random.uniform(0.5, 48), 1),  # hours
                    "region": region
                })
    
    return {
        "regulatory_heatmap": heatmap_data,
        "audit_trail": sorted(audit_data, key=lambda x: x["timestamp"], reverse=True),
        "exceptions": exception_data
    }

def generate_strategy_data(asset_classes: List[str] = None, time_period: str = "1M",
                          currencies: List[str] = None, min_volume: float = 0, **kwargs):
    """Generate trading strategy and market microstructure data."""
    if not asset_classes:
        asset_classes = get_all_asset_classes()
    if not currencies:
        currencies = get_all_currencies()
    
    days = get_days_from_period(time_period)
    dates, _ = generate_time_series(days)
    
    # Arbitrage Opportunities
    arbitrage_data = []
    strategies = ["Statistical Arbitrage", "Merger Arbitrage", "Index Arbitrage", 
                 "Calendar Spread", "Cross-Currency Arbitrage"]
    
    for strategy in strategies:
        for i in range(random.randint(5, 15)):
            opportunity_size = random.uniform(10000, 1000000)
            if opportunity_size >= min_volume:
                arbitrage_data.append({
                    "strategy": strategy,
                    "asset_class": random.choice(asset_classes),
                    "opportunity_size": round(opportunity_size, 2),
                    "expected_return": round(random.uniform(0.01, 0.25), 4),
                    "risk_score": round(random.uniform(1, 10), 1),
                    "duration": random.choice(["Intraday", "1-3 Days", "1 Week", "1 Month"]),
                    "confidence": round(random.uniform(0.6, 0.95), 2)
                })
    
    # Market Sentiment
    sentiment_data = []
    sentiment_sources = ["News", "Social Media", "Analyst Reports", "Options Flow", "Insider Trading"]
    
    for date in dates[-30:]:  # Last 30 days
        for source in sentiment_sources:
            sentiment_data.append({
                "date": date,
                "source": source,
                "sentiment_score": round(random.uniform(-1, 1), 3),
                "volume": random.randint(100, 10000),
                "relevance": round(random.uniform(0.3, 1.0), 2),
                "asset_class": random.choice(asset_classes)
            })
    
    # Liquidity Fragmentation
    fragmentation_data = []
    venues = ["NYSE", "NASDAQ", "BATS", "IEX", "Dark Pool 1", "Dark Pool 2", "Electronic ECN"]
    instruments = ["Large Cap", "Mid Cap", "Small Cap", "ETFs", "Fixed Income"]
    
    for instrument in instruments:
        total_volume = random.uniform(1000000, 10000000)
        remaining_volume = total_volume
        
        for venue in venues:
            if remaining_volume <= 0:
                break
            
            venue_volume = min(remaining_volume, random.uniform(0, remaining_volume * 0.4))
            remaining_volume -= venue_volume
            
            if venue_volume > 0:
                fragmentation_data.append({
                    "instrument": instrument,
                    "venue": venue,
                    "volume": round(venue_volume, 2),
                    "market_share": round((venue_volume / total_volume) * 100, 1),
                    "avg_trade_size": round(random.uniform(100, 10000), 2),
                    "spread": round(random.uniform(0.001, 0.01), 4)
                })
    
    return {
        "arbitrage": arbitrage_data,
        "sentiment": sentiment_data,
        "liquidity_fragmentation": fragmentation_data
    }

def generate_risk_metrics(counterparty_types: List[str] = None, 
                         risk_levels: List[str] = None,
                         time_period: str = "1M", region: str = "Global", **kwargs):
    """Generate comprehensive risk metrics and stress testing data."""
    if not counterparty_types:
        counterparty_types = get_all_counterparty_types()
    if not risk_levels:
        risk_levels = get_all_risk_levels()
    
    days = get_days_from_period(time_period)
    dates, _ = generate_time_series(days)
    
    # Value at Risk (VaR) by counterparty
    var_data = []
    counterparties = generate_counterparties(counterparty_types, region)
    
    for cp in counterparties[:10]:  # Limit to 10 counterparties
        var_1d = random.uniform(100000, 5000000)
        var_10d = var_1d * random.uniform(2.5, 4.0)  # 10-day VaR is typically higher
        
        var_data.append({
            "counterparty": cp,
            "var_1d": round(var_1d, 2),
            "var_10d": round(var_10d, 2),
            "expected_shortfall": round(var_1d * random.uniform(1.2, 1.8), 2),
            "confidence_level": 0.99,
            "risk_level": random.choice(risk_levels),
            "region": region
        })
    
    # Stress Test Scenarios
    stress_scenarios = [
        "2008 Financial Crisis", "COVID-19 Pandemic", "Brexit Vote",
        "Interest Rate Shock", "Credit Spread Widening", "Equity Market Crash"
    ]
    
    stress_data = []
    for scenario in stress_scenarios:
        for cp in counterparties[:5]:
            base_loss = random.uniform(1000000, 50000000)
            stress_data.append({
                "scenario": scenario,
                "counterparty": cp,
                "potential_loss": round(base_loss, 2),
                "probability": round(random.uniform(0.01, 0.15), 3),
                "time_horizon": random.choice(["1 Month", "3 Months", "1 Year"]),
                "severity": random.choice(risk_levels)
            })
    
    # Risk Concentration
    concentration_data = []
    risk_factors = ["Interest Rate", "Credit Risk", "Operational Risk", 
                   "Market Risk", "Liquidity Risk", "Concentration Risk"]
    
    for factor in risk_factors:
        total_exposure = random.uniform(10000000, 100000000)
        concentration_data.append({
            "risk_factor": factor,
            "total_exposure": round(total_exposure, 2),
            "top_10_concentration": round(random.uniform(0.3, 0.8), 2),  # % of total
            "risk_score": round(random.uniform(1, 10), 1),
            "regulatory_limit": round(random.uniform(0.6, 0.9), 2),
            "status": random.choice(["Within Limits", "Approaching Limit", "Limit Breach"])
        })
    
    return {
        "var_metrics": var_data,
        "stress_tests": stress_data,
        "risk_concentration": concentration_data
    }

# Utility functions for parameter discovery
def get_available_parameters():
    """Get all available parameter types and their options."""
    return {
        "time_periods": ["1D", "1W", "1M", "3M", "6M", "1Y", "YTD"],
        "asset_classes": get_all_asset_classes(),
        "counterparty_types": get_all_counterparty_types(),
        "regions": get_all_regions(),
        "risk_levels": get_all_risk_levels(),
        "currencies": get_all_currencies(),
        "settlement_types": get_all_settlement_types(),
        "regulatory_frameworks": get_all_regulatory_frameworks()
    }

def get_function_parameters(function_name: str):
    """Get available parameters for a specific generator function."""
    function_params = {
        "generate_trade_volumes": ["time_period", "asset_classes", "min_volume", "region"],
        "generate_anomalies": ["severity", "asset_classes", "counterparty_types", "time_period"],
        "generate_counterparty_exposures": ["counterparty_types", "risk_levels", "min_exposure", "region"],
        "generate_compliance_alerts": ["regulatory_scope", "severity", "entity_type", "time_period"],
        "generate_treasury_volumes": ["time_period", "currencies", "min_volume", "region"],
        "generate_repo_rates": ["time_period", "currencies", "region"],
        "generate_settlement_fails": ["settlement_types", "asset_classes", "min_amount", "region"],
        "generate_dealer_activity": ["counterparty_types", "min_volume", "region", "time_period"],
        "generate_swap_notionals": ["currencies", "time_period", "min_notional", "region"],
        "generate_cds_spreads": ["time_period", "region", "risk_levels"],
        "generate_etf_flows": ["asset_classes", "time_period", "min_flow", "region"],
        "generate_short_interest": ["asset_classes", "region", "min_shares", "risk_levels"],
        "generate_derivatives_data": ["asset_classes", "currencies", "time_period", "min_notional"],
        "generate_equity_data": ["settlement_types", "currencies", "time_period", "region"],
        "generate_compliance_data": ["regulatory_frameworks", "entity_types", "time_period", "region"],
        "generate_strategy_data": ["asset_classes", "time_period", "currencies", "min_volume"],
        "generate_risk_metrics": ["counterparty_types", "risk_levels", "time_period", "region"]
    }
    
    return function_params.get(function_name, [])