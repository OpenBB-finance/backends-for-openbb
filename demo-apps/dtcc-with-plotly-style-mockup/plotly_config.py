"""
Plotly configuration for DTCC OpenBB Dashboard with official DTCC branding colors.
"""

import plotly.graph_objects as go

# DTCC Official Brand Colors
DTCC_COLORS = {
    'primary_orange': '#ED6D3C',    # Core orange tone - accent buttons, highlights
    'primary_green': '#0E5447',     # Prominent navigation, accent elements
    'orange_light': '#F28352',      # Lighter orange variant/tint for hover states
    'green_dark': '#0B413A',        # Darker green variant for hover/shadow states
    'gallery': '#EBEBEB',           # Neutral off-white/light tone
    'cream': '#F8F6F3',             # Cream/off-white neutral background
    'dark_grey': '#2E2E2E',         # Dark tone for text/contrast
    'light_grey': '#8E8E8E',        # Medium grey for secondary text
}

def get_dtcc_palette():
    """Get DTCC color palette for charts."""
    return [
        DTCC_COLORS['primary_orange'],  # Primary - Core orange
        DTCC_COLORS['primary_green'],   # Secondary - Core green/teal
        DTCC_COLORS['orange_light'],    # Tertiary - Light orange variant
        DTCC_COLORS['green_dark'],      # Quaternary - Dark green variant
        '#F4946B',                      # Fifth - Even lighter orange
        '#236B5C',                      # Sixth - Medium green
        '#D96343',                      # Seventh - Medium orange
        '#174A3E',                      # Eighth - Alternative green shade
    ]

def get_theme_colors(theme='dark'):
    """Get DTCC color configuration for light and dark themes."""
    if theme == 'dark':
        return {
            'text': '#FFFFFF',
            'bg_color': '#151518',        # OpenBB dark background
            'paper_bg': '#151518',       # OpenBB dark background
            'grid_color': 'rgba(255, 255, 255, 0.1)',
            'zeroline_color': 'rgba(255, 255, 255, 0.2)',
            'line_color': DTCC_COLORS['primary_orange'],
            'main_line': DTCC_COLORS['primary_orange'],
            'positive_color': DTCC_COLORS['primary_green'],
            'negative_color': DTCC_COLORS['primary_orange'],
            'neutral': DTCC_COLORS['orange_light'],
            'neutral_color': DTCC_COLORS['primary_green'],
            'hover_bg': 'rgba(0, 0, 0, 0.8)',
            'legend_bg': 'rgba(0, 0, 0, 0.7)',
            'legend_border': f"rgba(237, 109, 60, 0.3)",
            'grid': 'rgba(255, 255, 255, 0.1)',
            'heatmap': {
                'zmid': 0,
                'text_color': '#FFFFFF'
            },
            'palette': get_dtcc_palette()
        }
    else:  # light theme
        return {
            'text': DTCC_COLORS['dark_grey'],
            'bg_color': '#FFFFFF',       # OpenBB light background (white)
            'paper_bg': '#FFFFFF',      # OpenBB light background (white)
            'grid_color': 'rgba(0, 0, 0, 0.15)',
            'zeroline_color': 'rgba(0, 0, 0, 0.25)',
            'line_color': DTCC_COLORS['primary_orange'],
            'main_line': DTCC_COLORS['primary_orange'],
            'positive_color': DTCC_COLORS['primary_green'],
            'negative_color': DTCC_COLORS['primary_orange'],
            'neutral': DTCC_COLORS['primary_green'],
            'neutral_color': DTCC_COLORS['orange_light'],
            'hover_bg': 'rgba(255, 255, 255, 0.95)',
            'legend_bg': 'rgba(255, 255, 255, 0.9)',
            'legend_border': f"rgba(237, 109, 60, 0.2)",
            'grid': 'rgba(0, 0, 0, 0.1)',
            'heatmap': {
                'zmid': 0,
                'text_color': DTCC_COLORS['dark_grey']
            },
            'palette': get_dtcc_palette()
        }


def base_layout(x_title=None, y_title=None, theme='dark', margin=None, height=None, show_title=False, watermark=True):
    """Create base layout configuration for DTCC branded charts."""
    colors = get_theme_colors(theme)
    
    # Optimized margins for dashboard widgets (no title space needed)
    default_margin = {'l': 50, 'r': 50, 't': 20, 'b': 50, 'pad': 0}
    if margin:
        default_margin.update(margin)
    
    layout = {
        'plot_bgcolor': colors['bg_color'],
        'paper_bgcolor': colors['paper_bg'],
        'font': {
            'color': colors['text'], 
            'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'size': 12
        },
        'showlegend': True,
        'hovermode': 'closest',
        'margin': default_margin,
        'colorway': colors['palette'],  # Use DTCC color palette
        'xaxis': {
            'title': {'text': x_title, 'font': {'color': colors['text'], 'size': 11}} if x_title else None,
            'gridcolor': colors['grid_color'],
            'zeroline': True,
            'zerolinecolor': colors['zeroline_color'],
            'tickfont': {'color': colors['text'], 'size': 10},
            'linecolor': colors['grid_color'],
            'linewidth': 1
        },
        'yaxis': {
            'title': {'text': y_title, 'font': {'color': colors['text'], 'size': 11}} if y_title else None,
            'gridcolor': colors['grid_color'],
            'tickfont': {'color': colors['text'], 'size': 10},
            'linecolor': colors['grid_color'],
            'linewidth': 1
        },
        'legend': {
            'orientation': 'v',
            'yanchor': 'top',
            'y': 0.98,
            'xanchor': 'right',
            'x': 0.98,
            'bgcolor': colors['legend_bg'],
            'bordercolor': colors['legend_border'],
            'borderwidth': 1,
            'font': {'color': colors['text'], 'size': 10}
        }
    }
    
    # Add DTCC watermark as background image
    if watermark:
        layout['images'] = [
            {
                'source': 'https://d2pasa6bkzkrjd.cloudfront.net/_resize/consensus2025/partner/500/site/consensus2025/images/userfiles/partners/15d6a0492f47a15733c125af54845766.png',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,  # Center horizontally
                'y': 0.5,  # Center vertically
                'sizex': 0.6,
                'sizey': 0.6,
                'xanchor': 'center',
                'yanchor': 'middle',
                'opacity': 0.15,  # Semi-transparent watermark
                'layer': 'below'  # Behind the chart data
            }
        ]
    
    # Never show main title on charts (handled by OpenBB widget system)
    layout['title'] = None
    
    if height:
        layout['height'] = height
        
    return layout


def create_line_trace(x_data, y_data, name, theme='dark', color=None, dash=None, width=2):
    """Create a line trace with DTCC branded styling."""
    colors = get_theme_colors(theme)
    
    if not color:
        color = colors['line_color']  # Uses DTCC Jaffa by default
    
    line_config = {'color': color, 'width': width}
    if dash:
        line_config['dash'] = dash
    
    return go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        name=name,
        line=line_config,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'X: %{x}<br>' +
                     'Y: %{y}<br>' +
                     '<extra></extra>'
    )


def create_vertical_line_trace(x_value, y_range, name, theme='dark', color=None):
    """Create a vertical line trace with DTCC branded markers."""
    colors = get_theme_colors(theme)
    
    if not color:
        if 'current' in name.lower() or 'actual' in name.lower():
            color = DTCC_COLORS['primary_orange']  # Primary color for current/actual
        elif 'target' in name.lower() or 'consensus' in name.lower():
            color = DTCC_COLORS['primary_green']   # Secondary color for targets
        else:
            color = colors['neutral_color']
    
    return go.Scatter(
        x=[x_value, x_value],
        y=y_range,
        mode='lines',
        name=name,
        line={'color': color, 'dash': 'dash', 'width': 2},
        showlegend=True,
        hoverinfo='skip'
    )


def create_dtcc_heatmap(z_data, x_labels, y_labels, theme='dark', colorscale=None):
    """Create a heatmap with DTCC branded colors."""
    if not colorscale:
        # DTCC branded colorscale from cream to orange to green
        colorscale = [
            [0.0, DTCC_COLORS['cream']],
            [0.3, DTCC_COLORS['gallery']],
            [0.6, DTCC_COLORS['primary_orange']],
            [1.0, DTCC_COLORS['primary_green']]
        ]
    
    colors = get_theme_colors(theme)
    
    return go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        showscale=True,
        hovertemplate='<b>%{y}</b><br>' +
                     '%{x}<br>' +
                     'Value: %{z}<br>' +
                     '<extra></extra>',
        colorbar={
            'title': {'side': 'right', 'font': {'color': colors['text'], 'size': 10}},
            'tickfont': {'color': colors['text'], 'size': 9}
        }
    )


def get_dtcc_chart_colors():
    """Get DTCC color mapping for common chart elements."""
    return {
        # Primary data series colors (based on DTCC palette)
        'primary': DTCC_COLORS['primary_orange'],     # #ED6D3C - Core orange
        'secondary': DTCC_COLORS['primary_green'],    # #0E5447 - Core green/teal
        'tertiary': DTCC_COLORS['orange_light'],      # #F28352 - Light orange variant
        'quaternary': DTCC_COLORS['green_dark'],      # #0B413A - Dark green variant
        'fifth': '#F4946B',                           # Even lighter orange
        'sixth': '#236B5C',                           # Medium green
        'seventh': '#D96343',                         # Medium orange
        'eighth': '#174A3E',                          # Alternative green shade
        
        # Status colors aligned with DTCC brand
        'positive': DTCC_COLORS['primary_green'],     # Positive - Green/Teal
        'negative': DTCC_COLORS['primary_orange'],    # Negative - Orange  
        'neutral': DTCC_COLORS['orange_light'],       # Neutral - Light orange
        'warning': DTCC_COLORS['orange_light'],       # Warning - Light orange
        'info': DTCC_COLORS['green_dark'],            # Info - Dark green variant
        
        # Severity levels
        'critical': DTCC_COLORS['primary_orange'],    # Critical - Core orange
        'high': '#D96343',                            # High - Medium orange
        'medium': DTCC_COLORS['orange_light'],        # Medium - Light orange  
        'low': DTCC_COLORS['primary_green'],          # Low - Core green
        
        # Status states
        'active': DTCC_COLORS['primary_orange'],      # Active - Core orange
        'pending': DTCC_COLORS['orange_light'],       # Pending - Light orange
        'completed': DTCC_COLORS['primary_green'],    # Completed - Core green
        'failed': DTCC_COLORS['primary_orange'],      # Failed - Core orange
        'open': DTCC_COLORS['primary_orange'],        # Open - Core orange
        'resolved': DTCC_COLORS['primary_green'],     # Resolved - Core green
        'investigating': DTCC_COLORS['orange_light'], # Investigating - Light orange
        
        # Trend indicators
        'bullish': DTCC_COLORS['primary_green'],      # Bullish - Core green
        'bearish': DTCC_COLORS['primary_orange'],     # Bearish - Core orange
        'neutral_trend': DTCC_COLORS['orange_light']  # Neutral trend - Light orange
    }

def get_toolbar_config():
    """Get standard toolbar configuration for Plotly charts."""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'pan2d',
            'lasso2d',
            'select2d',
            'autoScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toggleSpikelines'
        ],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'chart',
            'height': 500,
            'width': 800,
            'scale': 1
        }
    }


def format_hover_text(price, rank, change, fy2_pe, fy3_pe, consensus_prob, mc_prob):
    """Format hover text consistently across charts."""
    return (
        f"<b>Price: ${price:.2f}</b><br>"
        f"Rank: {rank:.0f}<br>"
        f"Change: {change:.2f}%<br>"
        f"Implied FY2 PE: {fy2_pe:.2f}<br>"
        f"Implied FY3 PE: {fy3_pe:.2f}<br>"
        f"Probability at or above (consensus cdf): {consensus_prob:.2f}%<br>"
        f"Probability at or above (Monte Carlo): {mc_prob:.1f}%"
    )