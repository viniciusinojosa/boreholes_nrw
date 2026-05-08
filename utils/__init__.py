"""Utility functions for downloading and visualising NRW borehole stratigraphy."""

from .geometry import (
    bbox_from_area_input,
    bbox_from_shapefile,
    bbox_from_wkt,
    force_point_geometry,
)
from .wfs import download_all_layers, download_borehole_headers, parse_borehole_layers
from .processing import build_3d_geodataframe, expand_layers_to_fixed_grid
from .plotting import create_3d_plot,save_3d_plot

__all__ = [
    "bbox_from_area_input",
    "bbox_from_shapefile",
    "bbox_from_wkt",
    "force_point_geometry",
    "download_borehole_headers",
    "download_all_layers",
    "parse_borehole_layers",
    "expand_layers_to_fixed_grid",
    "build_3d_geodataframe",
    "create_3d_plot",
]
