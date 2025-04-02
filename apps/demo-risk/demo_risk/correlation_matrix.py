from numpy import ones_like, triu
from plotly.graph_objs import Figure, Heatmap, Layout
from pandas import DataFrame, Series


def z_score_standardization(data: Series) -> Series:
    """Z-Score Standardization Method."""
    return (data - data.mean()) / data.std()


def correlation_matrix(
    data, chart: bool = True, theme: str = "dark"
) -> DataFrame | Figure:
    """Correlation Matrix Chart."""
    df = DataFrame(data)

    if "Date" in df.columns:
        df = df.set_index("Date")

    for col in df.columns:
        if col == "Date":
            continue
        df[col] = z_score_standardization(df[col])

    corr = df.corr()

    X = corr.columns.to_list()
    x_replace = X[-1]
    Y = X.copy()
    y_replace = Y[0]
    X = [x if x != x_replace else "" for x in X]
    Y = [y if y != y_replace else "" for y in Y]
    mask = triu(ones_like(corr, dtype=bool))
    df = corr.mask(mask)

    if chart is False:
        return df

    title = ""
    text_color = "white" if theme == "dark" else "black"
    colorscale = "RdBu"

    heatmap = Heatmap(
        z=df,
        x=X,
        y=Y,
        xgap=1,
        ygap=1,
        colorscale=colorscale,
        colorbar=dict(
            orientation="v",
            x=0.9,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            xref="container",
            yref="paper",
            len=0.66,
            bgcolor="rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)",
        ),
        text=df.fillna(""),
        texttemplate="%{text:.4f}",
        hoverongaps=False,
        hovertemplate="%{x} - %{y} : %{z:.4f}<extra></extra>",
    )
    layout = Layout(
        title_text=title,
        title_font_size=20,
        title_x=0.5,
        title_y=0.97,
        title_yanchor="top",
        xaxis=dict(
            showgrid=False,
            showline=False,
            ticklen=5,
            tickangle=90,
            automargin=False,
            ticklabelstandoff=10,
        ),
        yaxis=dict(
            showgrid=False,
            side="left",
            autorange="reversed",
            showline=False,
            ticklen=5,
            automargin="height+width+left",
            tickmode="auto",
            ticklabelstandoff=10,
        ),
        dragmode="pan",
        paper_bgcolor=(
            "rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)"
        ),
        font=dict(color=text_color),
        margin=dict(t=50, b=75, l=75, r=50),
    )
    fig = Figure(data=[heatmap], layout=layout)

    return fig


def plot_factors(df, color_df, X, Y, theme: str = "dark"):
    """
    Plot the factors of the data.
    """
    title = "Factors, Coefficients & P-Values"
    text_color = "white" if theme == "dark" else "black"

    custom_colorscale = [
        [0, "blue"],
        [0.05, "cyan"],
        [0.10, "orange"],
        [0.25, "red"],
        [1, "darkred"],
    ]

    heatmap = Heatmap(
        z=color_df,
        x=X,
        y=Y,
        xgap=1,
        ygap=1,
        colorscale=custom_colorscale,
        showscale=False,
        colorbar=dict(
            orientation="v",
            x=0.9,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            xref="container",
            yref="paper",
            len=0.66,
            bgcolor="rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)",
        ),
        text=df.fillna(""),
        texttemplate="%{text:.6f}",
        hoverongaps=False,
        hovertemplate="%{x} - %{y}<br>Coefficient: %{text:.6f}<br>P-Value: %{z:.6f}<extra></extra>",
    )

    layout = Layout(
        title_text=title,
        title_font_size=20,
        title_x=0.5,
        title_y=0.97,
        title_yanchor="top",
        xaxis=dict(
            showgrid=False,
            showline=False,
            ticklen=5,
            tickangle=0,
            side="top",
            automargin=True,
            tickfont=dict(size=12),
            ticklabelstandoff=10,
        ),
        yaxis=dict(
            showgrid=False,
            side="left",
            autorange="reversed",
            showline=False,
            ticklen=5,
            automargin="height+width+left",
            tickmode="auto",
            tickfont=dict(size=12),
            ticklabelstandoff=10,
        ),
        dragmode="pan",
        paper_bgcolor=(
            "rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,1)" if text_color == "white" else "rgba(255,255,255,1)"
        ),
        font=dict(color=text_color),
        margin=dict(t=75, b=50, l=85, r=50),
    )
    fig = Figure(data=[heatmap], layout=layout)

    return fig
