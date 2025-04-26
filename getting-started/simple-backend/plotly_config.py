"""
Plotly config settings for consistent chart behavior.

This module provides standardized configuration options for Plotly charts,
ensuring consistent interactivity, responsiveness, and appearance.
"""

def create_base_layout(
    x_title: str, 
    y_title: str, 
    y_dtype: str = ".2s", 
    theme: str = "dark"
):
    """
    Creates a base layout for a Plotly chart with customizable axis titles and
    y-axis formatting.

    Parameters:
    - x_title (str): The title for the x-axis. If the title is a date-related
      term, it will be set to None.
    - y_title (str): The title for the y-axis.
    - y_dtype (str): Optional. Specifies the format of the y-axis labels.
      Default is ".2s".
      Available options include:
      - ".2s": Short scale formatting with two significant digits (e.g., 1.2K).
      - ".2f": Fixed-point notation with two decimal places (e.g., 1234.56).
      - ".0f": Fixed-point notation with no decimal places (e.g., 1235).
      - ".0%": Percentage with no decimal places (e.g., 50%).
      - ".2%": Percentage with two decimal places (e.g., 50.00%).
      - "$,.2f": Currency format with two decimal places and comma as 
        thousand separator (e.g., $1,234.56).
      - ".2e": Scientific notation with two decimal places (e.g., 1.23e+3).
    - theme (str): Optional. The theme to use, either "light" or "dark".
      Default is "dark".

    Returns:
    - dict: A dictionary representing the layout configuration for a Plotly chart.
    """
    # Define colors based on theme
    if theme == "light":
        text_color = "#333333"  # Dark gray for light theme
        legend_text_color = "#000000"  # Black for legend text in light mode
        grid_color = "rgba(128, 128, 128, 0.2)"
        paper_bgcolor = "rgba(255,255,255,0)"  # Transparent white
        plot_bgcolor = "rgba(255,255,255,0)"  # Transparent white
        hoverlabel_bgcolor = "black"
        hoverlabel_font_color = "white"
        legend_bgcolor = "rgba(255, 255, 255, 0.9)"  # Opaque white background
        legend_bordercolor = "#666666"  # Dark gray border
    else:  # dark theme (default)
        text_color = "#ffffff"  # White for dark theme
        legend_text_color = text_color  # Same as text color for dark mode
        grid_color = "rgba(128, 128, 128, 0.2)"
        paper_bgcolor = "rgba(0,0,0,0)"  # Transparent black
        plot_bgcolor = "rgba(0,0,0,0)"  # Transparent black
        hoverlabel_bgcolor = "white"
        hoverlabel_font_color = "black"
        legend_bgcolor = "rgba(0, 0, 0, 0.7)"  # Semi-transparent black
        legend_bordercolor = "#444444"  # Light gray border

    if x_title.lower() in ['date', 'time', 'timestamp', 'datetime']:
        x_title = None
    return dict(
        title=None,
        xaxis=dict(
            title=x_title,
            showgrid=False,  # Remove x-axis gridlines
            color=text_color,
        ),
        yaxis=dict(
            title=y_title,
            showgrid=True,  # Show primary y-axis gridlines
            gridcolor=grid_color,
            color=text_color,
            tickformat=y_dtype
        ),
        yaxis2=dict(
            showgrid=False,  # Hide secondary y-axis gridlines
            color=text_color,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  # Position above the plot
            xanchor="center",
            x=0.5,  # Center the legend
            font=dict(color=legend_text_color),  # Use dedicated legend text color
            bgcolor=legend_bgcolor,  # Add background color
            bordercolor=legend_bordercolor,  # Add border color
            borderwidth=1,  # Add border width
        ),
        margin=dict(b=0, l=0, r=0, t=0),  # Adjust margin for the title
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        font=dict(color=text_color),
        hovermode="x unified",  # Put all hover data on the same x-axis
        hoverlabel=dict(
            bgcolor=hoverlabel_bgcolor,
            font_color=hoverlabel_font_color
        )
    )


def get_default_config():
    """
    Returns the default configuration for all Plotly charts in the application.
    
    This configuration:
    - Enables responsive behavior for charts
    - Configures the mode bar with appropriate settings
    - Sets up standard interaction modes
    - Defines transition animations
    
    Returns:
        dict: A dictionary of Plotly configuration settings
    """
    return {
        # Display options
        'displayModeBar': True,  # Always show the mode bar
        'responsive': True,  # Make charts responsive to window size
        'scrollZoom': True,  # Enable scroll to zoom
        
        # Mode bar configuration
        'modeBarButtonsToRemove': [
            'lasso2d',  # Remove lasso selection tool
            'select2d',  # Remove box selection tool
            'autoScale2d',  # Remove auto scale
            'toggleSpikelines',  # Remove spike lines
            'hoverClosestCartesian',  # Remove closest point hover
            'hoverCompareCartesian'  # Remove compare hover
        ],
        'modeBarButtonsToAdd': [
            'drawline',
            'drawcircle',
            'drawrect',
            'eraseshape'
        ],
        
        # Interaction settings
        'doubleClick': 'reset+autosize',  # Double-click to reset view
        'showTips': True,  # Show tips for interactions
        
        # Other settings
        'watermark': False,
        'staticPlot': False,  # Enable interactivity
        'locale': 'en',
        'showAxisDragHandles': True,  # Show axis drag handles
        'showAxisRangeEntryBoxes': True,  # Show axis range entry boxes
    }


def get_chart_colors(theme="dark"):
    """
    Returns standard colors for chart elements based on the theme.
    
    Parameters:
        theme (str): The theme to use, either "light" or "dark"
    
    Returns:
        dict: A dictionary of color settings for various chart elements
    """
    if theme == "light":
        return {
            # Main chart line colors
            'text': '#2E5090',
            'main_line': '#2E5090',   # Navy blue for light theme
            'positive': '#00AA44',    # Forest green for positive values
            'negative': '#CC0000',    # Red for negative values
            'neutral': '#3366CC',     # Blue for neutral values
            'sma_line': 'black',      # SMA line color
            # Additional colors for multiple series
            'secondary': '#8C4646',   # Burgundy
            'tertiary': '#5F4B8B',    # Muted purple
            "quaternary": "#d3d3d3"
        }
    else:  # dark theme (default)
        return {
            # Main chart line colors
            'text': '#FF8000',
            'main_line': '#FF8000',   # orange
            'positive': '#00B140',    # green
            'negative': '#F4284D',    # red
            'neutral': '#2D9BF0',     # blue
            'sma_line': 'white',      # SMA line color
            # Additional colors for multiple series
            'secondary': '#9E69AF',   # purple
            'tertiary': '#00C2DE',    # teal
            "quaternary": "#d3d3d3"
        }


def get_layout_update(theme="dark"):
    """
    Returns standard layout updates to apply to all charts.
    
    This includes:
    - UI revision settings for maintaining state
    - Transition animations
    - Drag mode settings
    - Hover and click behavior
    
    Parameters:
        theme (str): The theme to use, either "light" or "dark"
    
    Returns:
        dict: A dictionary of layout settings to update Plotly charts
    """
    # Define color schemes based on theme
    if theme == "light":
        text_color = '#333333'
        grid_color = 'rgba(221, 221, 221, 0.3)'  # Very faded grid
        line_color = '#AAAAAA'
        tick_color = '#AAAAAA'
        bg_color = '#ffffff'  # More opaque background
        active_color = '#3366CC'  # Nice blue color for light theme
        # Black text for better contrast in light mode
        legend_text_color = '#000000'
        # Darker border for better visibility
        legend_border_color = '#ffffff'
    else:  # dark theme (default)
        text_color = '#FFFFFF'
        grid_color = 'rgba(51, 51, 51, 0.3)'  # Very faded grid
        line_color = '#444444'
        tick_color = '#444444'
        bg_color = '#151518'  # More opaque background
        active_color = '#FF8000'  # Orange color for dark theme
        legend_text_color = text_color  # Use the same text color
        legend_border_color = "#151518"  # Use the same border color
    
    return {
        'uirevision': 'constant',  # Maintains view state during updates
        'autosize': True,  # Enables auto-sizing for responsive behavior
        'dragmode': 'zoom',  # Sets default mode to zoom instead of pan
        'hovermode': 'closest',  # Improves hover experience
        'clickmode': 'event',  # Makes clicking more responsive
        'margin': {
            't': 50,  # Top margin - increase this for more modebar space
            'r': 30,  # Right margin
            'b': 40,  # Bottom margin
            'l': 40,  # Left margin
            'pad': 4   # Padding between the plotting area and the axis lines
        },
        'transition': {
            'duration': 50,  # Small transition for smoother feel
            'easing': 'cubic-in-out'  # Smooth easing function
        },
        'modebar': {
            'orientation': 'v',  # Vertical orientation for modebar
            'activecolor': active_color  # Active button color
        },
        'font': {
            'family': 'Arial, sans-serif',  # Sans-serif font
            'size': 12,
            'color': text_color  # Text color based on theme
        },
        'xaxis': {
            'rangeslider': {'visible': False},  # Disable rangeslider
            'autorange': True,  # Enable autorange
            'constrain': 'domain',  # Constrain to domain for better zoom
            'showgrid': True,  # Show vertical grid lines
            'gridcolor': grid_color,  # Very faded grid lines
            'linecolor': line_color,  # Axis line color based on theme
            'tickcolor': tick_color,  # Tick color based on theme
            'linewidth': 1,  # Match y-axis line width
            'mirror': True,  # Mirror axis to match y-axis
            'showline': False,  # Hide the axis line to remove the box
            'zeroline': False,  # Hide zero line to match y-axis
            'ticks': 'outside',  # Place ticks outside
            'tickwidth': 1  # Match y-axis tick width
        },
        'yaxis': {
            'autorange': True,  # Enable autorange
            'constrain': 'domain',  # Constrain to domain
            'fixedrange': False,  # Allow y-axis zooming
            'showgrid': True,  # Show horizontal grid lines
            'gridcolor': grid_color,  # Very faded grid lines
            'linecolor': line_color,  # Axis line color based on theme
            'tickcolor': tick_color,  # Tick color based on theme
            'linewidth': 1,  # Consistent line width
            'mirror': True,  # Mirror axis
            'showline': False,  # Hide the axis line to remove the box
            'zeroline': False,  # Hide zero line
            'ticks': 'outside',  # Place ticks outside
            'tickwidth': 1  # Consistent tick width
        },
        'legend': {
            # Legend text color with better contrast
            'font': {'color': legend_text_color},
            'bgcolor': bg_color,  # More opaque background
            'bordercolor': legend_border_color,  # Better visible border
            'borderwidth': 1  # Add border width for better visibility
        },
    }


def apply_config_to_figure(figure, theme="dark"):
    """
    Applies the default configuration and layout updates to a Plotly figure.
    
    Parameters:
        figure (plotly.graph_objects.Figure): The Plotly figure to configure
        theme (str): The theme to use, either "light" or "dark"
        
    Returns:
        tuple: (figure, config) where figure is the configured Plotly figure
               and config is the configuration dictionary
    """
    # Apply layout updates with the specified theme
    figure.update_layout(**get_layout_update(theme))
    
    # Return both the figure and the config
    return figure
