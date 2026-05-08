"""Plotly visualisation functions."""

from __future__ import annotations

import geopandas as gpd
import plotly.express as px


def create_3d_plot(
    gdf3d: gpd.GeoDataFrame,
    color_column: str = "rock_name",
    max_points: int | None = 100_000,
):
    """
    Create an interactive 3D Plotly scatter plot of borehole layers.

    Parameters
    ----------
    gdf3d : geopandas.GeoDataFrame
        GeoDataFrame containing x, y, z coordinates and stratigraphy attributes.

    color_column : str, optional
        Column used to color the 3D points.

    max_points : int or None, optional
        Maximum number of points to display in the 3D viewer.
        If the dataset is larger, a random sample is plotted.
        Set to None to plot all points.
    """

    if color_column not in gdf3d.columns:
        raise ValueError(
            f"'{color_column}' is not a column. Available columns: {list(gdf3d.columns)}"
        )

    plot_gdf = gdf3d.copy()

    if max_points is not None and len(plot_gdf) > max_points:
        plot_gdf = plot_gdf.sample(max_points, random_state=42)
        print(f"Plotting sampled data: {max_points} of {len(gdf3d)} points")

    fig = px.scatter_3d(
        plot_gdf,
        x="x",
        y="y",
        z="z",
        color=color_column,
        hover_data=[
            "id",
            "depth_from_m",
            "depth_to_m",
            "depth_mid_m",
            "rock_code",
            "rock_name",
        ],
        opacity=0.7,
        height=800,
    )

    fig.update_traces(marker={"size": 2})

    fig.update_layout(
        scene={
            "xaxis_title": "X [EPSG:25832]",
            "yaxis_title": "Y [EPSG:25832]",
            "zaxis_title": "Depth below ground surface [m]",
        }
    )

    return fig


def save_3d_plot(
    fig,
    output_html: str = "boreholes_3d.html",
):
    """
    Save a Plotly figure as a lighter HTML file.

    Using include_plotlyjs='cdn' avoids embedding the full Plotly library
    inside the HTML file.
    """

    fig.write_html(
        output_html,
        include_plotlyjs="cdn",
        full_html=True,
    )

    print(f"Saved 3D viewer to: {output_html}")
