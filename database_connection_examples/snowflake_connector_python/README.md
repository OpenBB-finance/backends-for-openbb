# Snowflake Connector Python Example

This is a simple backend demonstrating Snowflake connectivity using the snowflake-connector-python library.

## Features
This example includes two widgets:
1. A table widget displaying all views in a given schema
2. A line chart showing stock close prices from the public Finance & Economics dataset

The first widget demonstrates how to use an endpoint to populate dropdown options.

> **Note:** This example uses the Snowflake Connector library, not Snowpark.

## Data Source
This example uses public data from the [Finance & Economics](https://app.snowflake.com/marketplace/listing/GZTSZAS2KF7/snowflake-data-finance-economics) dataset available in the Snowflake Marketplace.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure Snowflake credentials:
```bash
cp .env.example .env
```
Edit the `.env` file with your Snowflake credentials. By default, this example connects to a specific database, but the connector can be modified to support multiple databases.
Your account will look like this: `*.us-east-1.snowflakecomputing.com`.

3. Start the backend server:
```bash
uvicorn main:app --reload --port 5401
```

## Documentation
For more information, see the [Snowflake Connector for Python documentation](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example).

