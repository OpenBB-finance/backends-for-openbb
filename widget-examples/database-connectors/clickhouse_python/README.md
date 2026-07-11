# ClickHouse Explorer for OpenBB Workspace

Explore ClickHouse sample datasets (UK Housing Prices & NYC Taxi Trips) inside [OpenBB Workspace](https://pro.openbb.co).

## Datasets

- **UK Housing Prices** — 27M+ property transactions from the UK Land Registry (1995–present)
- **NYC Taxi Trips** — 3M+ taxi rides with fares, distances, and pickup zones

## Setup

### 1. ClickHouse Cloud

1. Sign up at [clickhouse.cloud](https://clickhouse.cloud/) and create a new service
2. When the service is created, you'll be shown the connection credentials — **save the password**, it is only displayed once
3. Once the service is running, click **Connect** to find your connection details

### 2. Environment variables

```bash
cp .env.example .env
```

Edit `.env` with your ClickHouse credentials:

| Variable | Required | Default | Where to find |
|---|---|---|---|
| `CLICKHOUSE_HOST` | Yes | — | ClickHouse Cloud console → your service → **Connect** → the hostname (e.g. `abc123.us-east-1.aws.clickhouse.cloud`) |
| `CLICKHOUSE_PASSWORD` | Yes | — | Shown once when you create the service. If lost, reset it under **Settings** → **Reset password** |
| `CLICKHOUSE_PORT` | No | `8443` | Default HTTPS native port — no need to change unless your service uses a custom port |
| `CLICKHOUSE_USER` | No | `default` | The default admin user created with every ClickHouse Cloud service |

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Load sample data

```bash
python setup.py
```

The setup script reads `.env`, creates two databases (`uk` and `nyc_taxi`), and loads the sample datasets. The UK dataset (~27M rows) may take several minutes.

### 5. Start the server

```bash
uvicorn main:app --reload --port 7781
```

The server starts on `http://localhost:7781`.

### 6. Connect to OpenBB Workspace

1. Go to [pro.openbb.co](https://pro.openbb.co)
2. Add a custom backend with URL `http://localhost:7781`
3. Two dashboards will appear: **UK Housing Prices** and **NYC Taxi Trips**
