# Earnings Prep - OpenBB Platform Backend

A comprehensive earnings preparation backend for the OpenBB Platform that provides access to Boeing's earnings data, including production forecasts, delivery estimates, analyst price targets, earnings transcripts, and more.


## Python Installation

Install this in an environment with a version of Python between 3.11-3.12, inclusively.

```bash
# Install dependencies
pip install -e .

# Or using poetry
poetry install
```

## Running the Application

Start the server, locally, with:

```bash
demo_earningsprep
```

## OpenBB Platform Integration

1. **Open the OpenBB Workspace**

2. **Add Custom Backend**
   - Add `http://127.0.0.1:8055` as a new custom backend

3. **Select App**
   - Click on the new "Earnings Prep" application

5. **Enjoy your earnings prep demo!**

## Available Endpoints

- `/production` - Quarterly Production Forecasts
- `/deliveries` - Quarterly Delivery Forecasts  
- `/price_targets` - Analyst Price Targets
- `/transcripts` - Earnings Call Transcripts
- `/eight_k` - 8-K Earnings Announcements
- `/investor_presentations` - Investor Presentations
- `/price_action` - Earnings Call Price Action
- `/markets_eq_audio_analysis` - Audio Analysis
- `/markets_eq_research_report` - Research Reports

## Project Structure

```
earningsprep/
├── demo_earningsprep/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Pydantic data models
│   │   └── depends.py       # Dependency injection
│   ├── data/                # Static data files
│   │   ├── deliveries.csv   # Delivery forecasts
│   │   ├── production.csv   # Production forecasts
│   │   ├── transcripts.xz   # Earnings transcripts
│   │   └── ...
│   └── docs/                # PDF documents

```
## License

This project is licensed under the MIT License.
