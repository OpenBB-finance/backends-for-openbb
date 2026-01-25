# OpenBB App Builder

Build custom backends and widgets for [OpenBB Workspace](https://openbb.co/products/workspace) with AI assistance.

## What it does

This skill guides Claude through a complete pipeline for building OpenBB apps:

1. **Interview** - Gather requirements or analyze existing Streamlit/Gradio code
2. **Widget Design** - Define widget types, parameters, and columns
3. **Layout** - Design dashboard layout with tabs and groupings
4. **Plan** - Generate implementation plan
5. **Build** - Create FastAPI backend, widgets.json, apps.json
6. **Validate** - Run validation scripts
7. **Test** - Browser testing with OpenBB Workspace

## Installation

```bash
npx skills add OpenBB-finance/backends-for-openbb
```

## Usage

```
"Build an OpenBB app that shows crypto prices from CoinGecko"
```

```
"Convert this Streamlit app to OpenBB:
import streamlit as st
..."
```

```
"Quick mode: build a stock screener app"
```

## Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| Standard | (default) | Confirm at each phase |
| Quick | "quick mode" | Sensible defaults, minimal questions |
| Reference | Code snippets | Auto-analyze and convert |
| Verbose | "verbose" | Educational, detailed explanations |

## Features

- **Reference conversion**: Converts Streamlit, Gradio, Flask, FastAPI, React apps
- **Validation scripts**: Automated schema validation for widgets.json and apps.json
- **Browser testing**: Claude-in-Chrome integration for end-to-end testing
- **Error recovery**: Auto-fix common issues with retry logic

## Output

Creates a complete app directory:

```
{app-name}/
├── main.py            # FastAPI application
├── widgets.json       # Widget configurations
├── apps.json          # Dashboard layout
├── requirements.txt   # Dependencies
├── Dockerfile         # Docker configuration
└── .env.example       # Environment template
```

## Requirements

- Python 3.11+
- OpenBB Workspace account (free at [pro.openbb.co](https://pro.openbb.co))

## Links

- [OpenBB Workspace Docs](https://docs.openbb.co/workspace)
- [Backends for OpenBB Repository](https://github.com/OpenBB-finance/backends-for-openbb)
