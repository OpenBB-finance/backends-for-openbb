# Databricks Connector Python Example

A backend demonstrating Databricks connectivity using the [databricks-sql-connector](https://docs.databricks.com/en/dev-tools/python-sql-connector.html) library, structured as a multi-app OpenBB Workspace backend.

## Apps
The backend ships five apps (`apps.json`), one per sample dataset domain:

| App | Dataset | Highlights |
|---|---|---|
| NYC Taxi | `samples.nyctaxi` | Metric tiles, daily line chart, hourly column chart, raw trips table |
| Bakehouse Sales | `samples.bakehouse` | Product/city revenue, grouped product filter, markdown customer reviews |
| Wanderbricks Travel | `samples.wanderbricks` | Monthly bookings, top destinations, property types, country filter |
| TPC-H Supply Chain | `samples.tpch` | Yearly revenue, revenue by nation and market segment, region filter |
| Databricks SQL Explorer | whole catalog | Schema/table browser plus an **omni SQL widget** for ad-hoc read-only queries |

## Widget types demonstrated
- `metric` KPI tiles
- `table` with `chartView` (line, bar, column) and `columnsDefs` formatting
- `markdown` (customer reviews)
- `omni` with a SQL editor param (`"language": "sql"`), returning tables or markdown errors
- Dropdown params populated from endpoints (`optionsEndpoint`), shared across widgets via app-level param groups

## Data Source
All data comes from the built-in `samples` catalog that ships with every Databricks workspace (including the [Free Edition](https://www.databricks.com/learn/free-edition)). No data loading is required.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure Databricks credentials:
```bash
cp .env.example .env
```
Edit the `.env` file with your Databricks connection details:
- `DATABRICKS_SERVER_HOSTNAME`: your workspace hostname, e.g. `dbc-a1b2c3d4-e5f6.cloud.databricks.com`
- `DATABRICKS_HTTP_PATH`: the HTTP path of a SQL warehouse, e.g. `/sql/1.0/warehouses/abc123def456`
- `DATABRICKS_ACCESS_TOKEN`: a personal access token

You can find the hostname and HTTP path in your Databricks workspace under **SQL Warehouses → (your warehouse) → Connection details**, and create a personal access token under **Settings → Developer → Access tokens** (Free Edition requires identity verification before tokens can be created).

3. Start the backend server:
```bash
uvicorn main:app --reload --port 5402
```

Then add `http://localhost:5402` as a custom backend in OpenBB Workspace. The five apps appear under **Apps → My Apps**.

## Notes
- Query results are cached in-process for 5 minutes to keep the (2X-Small) serverless warehouse load minimal.
- The omni SQL widget only accepts single read-only statements (`SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`).

## Documentation
For more information, see the [Databricks SQL Connector for Python documentation](https://docs.databricks.com/en/dev-tools/python-sql-connector.html).
