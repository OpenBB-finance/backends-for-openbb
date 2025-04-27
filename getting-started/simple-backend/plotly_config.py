"""
Plotly config settings for consistent chart behavior.

This module provides standardized configuration options for Plotly charts,
ensuring consistent interactivity and appearance across all visualizations.
It handles theme management, layout configuration, and toolbar settings.
"""

def get_theme_colors(theme="dark"):
    """
    Get color scheme based on theme.
    
    This function defines a comprehensive color palette for both light and dark themes,
    including colors for text, backgrounds, hover states, and specific chart elements.
    The colors are chosen for optimal contrast and readability.
    
    Args:
        theme (str): Either "light" or "dark" theme selection
        
    Returns:
        dict: A dictionary containing color values for various chart elements
    """
    if theme == "light":
        return {
            # Light theme colors optimized for readability
            "text": "#333333",  # Dark gray for primary text
            "grid": "rgba(128, 128, 128, 0.2)",  # Semi-transparent grid lines
            "background": "rgba(255,255,255,0)",  # Transparent white background
            "hover_bg": "black",  # Black background for hover tooltips
            "hover_text": "white",  # White text for hover tooltips
            "legend_bg": "rgba(255, 255, 255, 0.9)",  # Semi-transparent legend background
            "legend_border": "#666666",  # Gray border for legend
            "main_line": "#2E5090",  # Blue for primary data lines
            "positive": "#00AA44",  # Green for positive values
            "negative": "#CC0000",  # Red for negative values
            "neutral": "#3366CC",  # Blue for neutral values
            "heatmap": {
                "colorscale": "RdBu_r",  # Red-Blue diverging colormap (reversed)
                "zmid": 0,  # Center point for diverging colormap
                "text_color": "#333333"  # Text color for heatmap annotations
            }
        }
    return {
        # Dark theme colors optimized for readability
        "text": "#ffffff",  # White for primary text
        "grid": "rgba(128, 128, 128, 0.2)",  # Semi-transparent grid lines
        "background": "rgba(0,0,0,0)",  # Transparent black background
        "hover_bg": "white",  # White background for hover tooltips
        "hover_text": "black",  # Black text for hover tooltips
        "legend_bg": "rgba(0, 0, 0, 0.7)",  # Semi-transparent legend background
        "legend_border": "#444444",  # Dark gray border for legend
        "main_line": "#FF8000",  # Orange for primary data lines
        "positive": "#00B140",  # Green for positive values
        "negative": "#F4284D",  # Red for negative values
        "neutral": "#2D9BF0",  # Blue for neutral values
        "heatmap": {
            "colorscale": "RdBu",  # Red-Blue diverging colormap
            "zmid": 0,  # Center point for diverging colormap
            "text_color": "#ffffff"  # Text color for heatmap annotations
        }
    }


def base_layout(x_title=None, y_title=None, y_dtype=".2s", theme="dark"):
    """
    Create a standardized layout for Plotly charts.
    
    This function generates a consistent layout configuration for all charts,
    handling axis formatting, legend positioning, and overall chart appearance.
    It automatically handles date/time axes and provides consistent styling.
    
    Args:
        x_title (str, optional): X-axis title. If None and axis represents date/time,
                                the title will be hidden
        y_title (str, optional): Y-axis title
        y_dtype (str): Y-axis number format (default: ".2s" for SI units)
        theme (str): "light" or "dark" theme selection
        
    Returns:
        dict: A complete Plotly layout configuration dictionary
    """
    colors = get_theme_colors(theme)
    
    # Remove x-axis title for date/time axes to avoid redundancy
    if x_title and x_title.lower() in ['date', 'time', 'timestamp', 'datetime']:
        x_title = None
        
    return {
        "title": None,  # No default title, should be set by the chart creator
        "xaxis": {
            "title": x_title,
            "showgrid": False,  # Hide x-axis grid for cleaner look
            "color": colors["text"]
        },
        "yaxis": {
            "title": y_title,
            "showgrid": True,  # Show y-axis grid for better readability
            "gridcolor": colors["grid"],
            "color": colors["text"],
            "tickformat": y_dtype  # Format numbers using SI units by default
        },
        "legend": {
            "orientation": "h",  # Horizontal legend
            "yanchor": "bottom",
            "y": 1.02,  # Position above the chart
            "xanchor": "center",
            "x": 0.5,  # Center horizontally
            "font": {"color": colors["text"]},
            "bgcolor": colors["legend_bg"],
            "bordercolor": colors["legend_border"],
            "borderwidth": 1
        },
        "margin": {"b": 0, "l": 0, "r": 0, "t": 0},  # Minimize margins
        "paper_bgcolor": colors["background"],
        "plot_bgcolor": colors["background"],
        "font": {"color": colors["text"]},
        "hovermode": "x unified",  # Show all data points at current x position
        "hoverlabel": {
            "bgcolor": colors["hover_bg"],
            "font_color": colors["hover_text"]
        }
    }


def get_toolbar_config():
    """
    Get standard Plotly configuration for the chart toolbar.
    
    This function defines the interactive features available in the chart toolbar,
    removing unnecessary buttons and setting up standard behaviors for better UX.
    
    Returns:
        dict: A complete Plotly configuration dictionary for the toolbar
    """
    return {
        "displayModeBar": True,  # Show the mode bar
        "responsive": True,  # Make chart responsive to container size
        "scrollZoom": True,  # Enable zooming with scroll wheel
        "modeBarButtonsToRemove": [
            "lasso2d",  # Remove lasso selection
            "select2d",  # Remove box selection
            "autoScale2d",  # Remove auto-scale
            "toggleSpikelines",  # Remove spike lines toggle
            "hoverClosestCartesian",  # Remove closest point hover
            "hoverCompareCartesian"  # Remove compare hover
        ],
        "doubleClick": "reset+autosize",  # Reset zoom and autosize on double click
        "showTips": True,  # Show tooltips for toolbar buttons
        "watermark": False,  # Hide Plotly watermark
        "staticPlot": False,  # Enable interactivity
        "locale": "en"  # Set English as default language
    }
