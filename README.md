# OpenBB Workspace

## Introduction

An OpenBB Workspace Data Integration is a versatile way to connect your data to widgets inside OpenBB Workspace. Whether hosted internally or externally, this method provides a standardized structure that OpenBB Workspace widgets can read and then display any data.

Note: Most of the examples provided use Python FastAPI due to our familiarity with the library, but the same could be done utilizing different languages.

The Main tenants are:

1. **Data returned should be in JSON format** (Note : you can utilize the "dataKey" variable in the widgets.json if you have nested JSON.)

<details>
    <summary>Example JSON</summary>

    ```json
    [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "price": 150.5,
        "marketCap": 2500000000,
        "change": 1.25
      },
      {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 2800.75,
        "marketCap": 1900000000,
        "change": -0.75
      },
      {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "price": 300.25,
        "marketCap": 220000000,
        "change": 0.98
      },
    ]
    ```

</details>

2. **An endpoint returning a ```widgets.json``` file** : This file defines widget properties such as name, description, category, type, endpoint, and other information. Each widget will be defined in this file – You can find the format in any of the templates folder with a detailed definition below.

3. **CORS Enabled** : If hosting locally you must enable [CORS](https://fastapi.tiangolo.com/tutorial/cors/).

4. **Adding Authentication (optional)** : If your backend requires authentication we offer the ability to set a query param or header when you connect to it through OpenBB Pro. These values are sent on every request when configured. If you require another method - please reach out to us.

## Getting Started

We recommend starting with the [getting-started/hello-world](getting-started/hello-world/README.md) example. Then Moving on to the [getting-started/reference-backend](getting-started/reference-backend/README.md).

This will give you a good understanding of how to setup your own backend and connect it to OpenBB Workspace.

## Supported Integrations and Apps

Each Integration below has a folder which contains an example of different implementations - We recommend starting with the Table Widget Example.

### Apps

| App | Description |
| ----------- | ----------- |
| [demo-risk](/demo-apps/demo-risk/README.md) | A simple risk app |
| [dtcc_trade_repository](/demo-apps/dtcc_trade_repository/README.md) | A simple trade repository app |

### Widgets

| Integration | Description |
| ----------- | ----------- |
| [Table Widget](/widget-examples/widget-types/table-widget) | A simple table widget from a file or endpoint |
| [Chart Widget](/widget-examples/widget-types/chart-widget) | How to return a plotly chart or a built in chart |
| [Markdown Widget](/widget-examples/widget-types/markdown-widget) | Markdown Widget and example with a parameter |
| [Metric Widget](/widget-examples/widget-types/metric-widget) | Showing a single metric |
| [Multi File Viewer](/widget-examples/widget-types/multi-file-viewer) | How to return a multi file viewer |
| [PDF Widget](/widget-examples/widget-types/pdf-widget) | How to return a PDF file |
| [News Widget](/widget-examples/widget-types/news-widget) | How to return a news widget |
| [Advanced Charting](/widget-examples/widget-types/advanced-charting) | How to return an advanced chart |
| [Live Grid](/widget-examples/widget-types/live-grid) | How to return a live grid |

### Parameters

| Parameter Examples | Description |
| ----------- | ----------- |
| [Parameters Widget](/widget-examples/parameter-types/parameters-example) | Example of setting up widgets with parameters |
| [Grouping Widgets](/widget-examples/parameter-types/grouping_widgets) | How to group widgets on the dashboard |
| [Column and Cell Rendering](/widget-examples/parameter-types/column_and_cell_rendering) | An example of widgets with custom column and cell rendering |
| [Form Parameters](/widget-examples/parameter-types/form-parameters) | How to return a form parameter |

### Database Connectors

| Database Connection Examples | Description |
| ----------- | ----------- |
| [ClickHouse](/widget-examples/database-connectors/clickhouse_python/README.md) | ClickHouse is an open-source column-oriented DBMS. |
| [Supabase](/widget-examples/database-connectors/supabase_python/README.md) | Supabase is an open source Firebase alternative. |
| [MindsDB](/widget-examples/database-connectors/mindsdb_python/README.md) | MindsDB is an open-source AI layer for existing databases. |
| [ElasticSearch](/widget-examples/database-connectors/elasticsearch_python/README.md) | Elasticsearch is a search engine based on the Lucene library. |
| [ArticDB](/widget-examples/database-connectors/articdb_python/README.md) | Using ArticDB to add data to a widget. |
| [Snowflake](/widget-examples/database-connectors/snowflake_connector_python/README.md) | Snowflake is a cloud-based data warehousing platform. |

For more examples on setting up your own App - you can head to our documentation at <https://docs.openbb.co/workspace>.
