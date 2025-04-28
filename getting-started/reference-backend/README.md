# OpenBB Workspace Backend Template

A comprehensive FastAPI application template for OpenBB Workspace that demonstrates various widget types and features.

## Setup

1. Install the required dependencies:

```bash
pip install fastapi uvicorn requests plotly
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
- Modular organization of endpoints and widgets

### Widget Registration Pattern

The application uses a decorator-based approach to register widgets, which combines the UI/UX configuration with the API endpoint implementation. This is achieved through the `@register_widget` decorator that:

- Defines the widget's appearance and behavior in the OpenBB Workspace UI
- Automatically registers the widget configuration in the `WIDGETS` registry
- Links the UI configuration directly to its corresponding API endpoint
- Maintains a single source of truth for widget definitions

### Available Widget Types

1. **Markdown Widgets**
   - Basic markdown display
   - Support for images (URL and local)
   - Error handling
   - Run button functionality
   - Auto-refresh capabilities
   - Stale time indicators

2. **Table Widgets**
   - Basic table display
   - Column definitions and formatting
   - Render functions (color coding, hover cards)
   - Chart integration
   - Time series visualization
   - API endpoint integration

3. **Chart Widgets**
   - Plotly integration
   - Theme support
   - Toolbar configuration
   - Heatmap visualization
   - TradingView integration

4. **Form Widgets**
   - Text input
   - Number input
   - Date picker
   - Boolean toggle
   - Dropdown selection
   - Multi-select options
   - Dependent dropdowns

5. **PDF Widgets**
   - Base64 encoded PDF display
   - URL-based PDF display
   - Multi-PDF viewer

### Widget Features

1. **Auto-refresh**
   - `refetchInterval`: Time between automatic refreshes
   - `staleTime`: Time after which data is considered stale
   - `runButton`: Manual refresh option

2. **Parameter Management**
   - Shared parameters between widgets
   - Dependent parameters
   - Parameter grouping
   - Default values
   - Validation

3. **Data Visualization**
   - Table formatting
   - Chart integration
   - Color coding
   - Hover information
   - Interactive elements

4. **Error Handling**
   - HTTP exception handling
   - Error messages
   - Status codes
   - User feedback

### API Endpoints

1. Core Endpoints:
   - `GET /`: Basic API information
   - `GET /widgets.json`: Widget configuration
   - `GET /templates.json`: Template configuration

2. Widget Endpoints:
   - Various widget-specific endpoints for different functionalities
   - Form submission endpoints
   - Data fetching endpoints
   - Configuration endpoints

### Security & Configuration

- CORS properly configured for OpenBB Workspace domain
- FastAPI metadata includes title, description, and version
- All endpoints documented with docstrings
- Input validation and error handling

## Best Practices

1. **Widget Organization**
   - Use categories and subcategories for better organization
   - Group related widgets together
   - Use consistent naming conventions

2. **Parameter Management**
   - Share parameters between related widgets
   - Use dependent parameters when appropriate
   - Provide clear descriptions and labels

3. **Error Handling**
   - Implement proper error handling
   - Provide meaningful error messages
   - Use appropriate HTTP status codes

4. **Performance**
   - Use appropriate refresh intervals
   - Implement stale time indicators
   - Optimize data fetching

5. **Security**
   - Validate all inputs
   - Handle errors gracefully
   - Use proper CORS configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
