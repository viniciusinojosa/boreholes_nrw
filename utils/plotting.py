"""Plotly visualisation functions."""

from __future__ import annotations

import geopandas as gpd
import plotly.express as px


def create_3d_plot(gdf3d: gpd.GeoDataFrame, color_column: str = "rock_name"):
    """Create an interactive 3D Plotly scatter plot of borehole layers."""
    if color_column not in gdf3d.columns:
        raise ValueError(
            f"'{color_column}' is not a column. Available columns: {list(gdf3d.columns)}"
        )

    fig = px.scatter_3d(
        gdf3d,
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
