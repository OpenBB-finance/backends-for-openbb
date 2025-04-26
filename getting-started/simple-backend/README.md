# Hello World

A simple FastAPI application for OpenBB Workspace.

## Setup

1. Install the required dependencies:

```bash
pip install fastapi uvicorn
```

2. Run the application:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 7779
```

The application will be available at `http://localhost:7779`

## Architecture

This FastAPI application is designed to work as a backend for OpenBB Workspace. Here's a breakdown of its architecture:

### Core Application Structure

- FastAPI backend service running on port 7779
- CORS enabled specifically for `https://pro.openbb.co`
- Widget registration using the `@register_widget` decorator pattern

### Widget Registration Pattern

The application uses a decorator-based approach to register widgets, which combines the UI/UX configuration with the API endpoint implementation. This is achieved through the `@register_widget` decorator that:

- Defines the widget's appearance and behavior in the OpenBB Workspace UI
- Automatically registers the widget configuration in the `WIDGETS` registry
- Links the UI configuration directly to its corresponding API endpoint
- Maintains a single source of truth for widget definitions

Example from the code:
```python
@register_widget({
    "name": "Hello World",
    "description": "A simple markdown widget that displays Hello World",
    "category": "Hello World",
    "type": "markdown",
    "endpoint": "hello_world",
    "gridData": {"w": 12, "h": 4},
    "params": [
        {
            "paramName": "name",
            "value": "",
            "label": "Name",
            "type": "text",
            "description": "Enter your name"
        }
    ]
})
@app.get("/hello_world")
def hello_world(name: str = ""):
    return f"# Hello World {name}"
```

### API Endpoints

1. `GET /`
   - Simple root endpoint returning basic application info
   - Returns: `{"Info": "Hello World example"}`

2. `GET /widgets.json`
   - Serves the widget configuration for OpenBB Workspace
   - Returns the automatically registered widgets from the `WIDGETS` registry
   - Configuration is maintained through the `@register_widget` decorator

3. `GET /templates.json`
   - Serves the templates configuration for OpenBB Workspace
   - Reads and returns the contents of `templates.json`
   - Defines available templates for the OpenBB Workspace UI

4. `GET /hello_world`
   - Main functional endpoint returning a personalized greeting
   - Accepts an optional `name` parameter
   - Returns a markdown-formatted greeting message
   - Widget configuration is defined through the `@register_widget` decorator

### Templates Configuration

The templates are configured in `templates.json` with the following properties:
- Defines pre-configured layouts and widget arrangements
- Allows users to quickly set up common workspace configurations
- Templates can include:
  - Multiple widgets with specific positions
  - Pre-configured widget parameters
  - Custom layouts for different use cases
  - Widget grouping for organized workspace management
- Templates are served through the `/templates.json` endpoint
- Users can select templates to quickly populate their workspace

> **Note:** Templates are typically not created through direct code implementation. Instead, you can configure widgets and layouts directly in the OpenBB Workspace interface. After setting up your desired configuration, right-click and select "Export Template" to generate the configuration file for backend use.

### Integration with OpenBB Workspace

- Designed as a plugin/widget for OpenBB Workspace
- Widget configuration is defined through the `@register_widget` decorator
- CORS configuration ensures secure access from OpenBB Workspace domain
- Widget appears in OpenBB Workspace UI for user interaction

### Security & Configuration

- CORS properly configured for OpenBB Workspace domain
- FastAPI metadata includes title, description, and version
- All endpoints documented with docstrings

This architecture follows a clean, modular design where:

- Backend (FastAPI) handles business logic
- Widget configuration is integrated with API endpoints through decorators
- Integration managed through standardized API endpoints and CORS
