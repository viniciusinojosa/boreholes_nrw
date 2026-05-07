"""Processing functions for borehole stratigraphic layers."""

from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd


def expand_layers_to_fixed_grid(df: pd.DataFrame, step: float = 0.1) -> pd.DataFrame:
    """Expand irregular stratigraphic intervals to a fixed-depth grid.

    Example: if ``step=0.1``, each borehole layer is discretised into 10 cm
    intervals while retaining the original lithological code and description.
    """
    rows = []

    for _, row in df.iterrows():
        start_i = int(np.floor(row["from_m"] / step))
        end_i = int(np.ceil(row["to_m"] / step))

        for i in range(start_i, end_i):
            depth_from = round(i * step, 2)
            depth_to = round((i + 1) * step, 2)
            depth_mid = round((depth_from + depth_to) / 2, 2)

            if depth_to <= row["from_m"] or depth_from >= row["to_m"]:
                continue

            rows.append(
                {
                    "id": row["feature_id"],
                    "depth_from_m": depth_from,
                    "depth_to_m": depth_to,
                    "depth_mid_m": depth_mid,
                    "rock_code": row["rock_code"],
                    "rock_name": row["rock_name"],
                }
            )

    return pd.DataFrame(rows)


def build_3d_geodataframe(
    headers_gdf: gpd.GeoDataFrame,
    layers_df: pd.DataFrame,
    step: float = 0.1,
) -> gpd.GeoDataFrame:
    """Join fixed-grid layers to borehole coordinates and add x/y/z columns."""
    layers_grid = expand_layers_to_fixed_grid(layers_df, step=step)
    layers_gdf = layers_grid.merge(headers_gdf[["id", "geometry"]], on="id", how="left")
    layers_gdf = gpd.GeoDataFrame(layers_gdf, geometry="geometry", crs=headers_gdf.crs)

    layers_gdf = layers_gdf.dropna(subset=["geometry"])
    layers_gdf["x"] = layers_gdf.geometry.x
    layers_gdf["y"] = layers_gdf.geometry.y
    layers_gdf["z"] = -layers_gdf["depth_mid_m"]

    return layers_gdf
