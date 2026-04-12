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

## Backend URL requirements

When you add a backend in OpenBB Workspace, use the root base URL for that backend.

- Expected: `http://192.168.1.100:7777`
- Expected: `https://vstocks.example.com`
- Not supported as the backend base URL: `https://example.com/vstock`

OpenBB Workspace expects to find `widgets.json` at:

```text
<base-url>/widgets.json
```

That means the backend configuration must be served from the root of the backend base URL.

If you are deploying on another machine in your LAN, make sure your app is listening on all interfaces, for example:

```bash
uvicorn main:app --host 0.0.0.0 --port 7777
```

If you need to serve additional application routes under a prefix such as `/vstock`, keep `widgets.json` at the backend root and put the rest of your routes behind the prefix. If your deployment requires a path prefix for the entire backend, use a dedicated host or subdomain instead of a subpath.

## Getting Started

We recommend starting with the [getting-started/hello-world](getting-started/hello-world/README.md) example.

Then Moving on to the [getting-started/reference-backend](getting-started/reference-backend/README.md).

This will give you a good understanding of how to setup your own backend and connect it to OpenBB Workspace.

### Leveraging AI

If you are utilizing a coding agent to build your OpenBB backend, we recommend:
- Utilizing the following MCP Server to enhance coding agent with OpenBB docs: [https://smithery.ai/server/@DidierRLopes/openbb-docs-mcp](https://smithery.ai/server/@DidierRLopes/openbb-docs-mcp)
- Or providing the entire documentation to the agent in markdown format by copy-pasting this link into context: [https://docs.openbb.co/workspace/llms-full.txt](https://docs.openbb.co/workspace/llms-full.txt).

For more examples on setting up your own App - you can head to our documentation at [https://docs.openbb.co/workspace](https://docs.openbb.co/workspace).

## Examples of apps

Check awesome open source OpenBB apps built by our team or by the community here: [https://github.com/OpenBB-finance/awesome-openbb](https://github.com/OpenBB-finance/awesome-openbb).
