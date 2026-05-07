"""Geometry helper functions."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
from shapely import wkt as shapely_wkt
from shapely.geometry import LineString, MultiLineString, Point


def force_point_geometry(geom):
    """Convert borehole geometries to point geometries.

    Some borehole features are returned as line-like geometries. For 3D
    stratigraphy plotting, one x/y position per borehole is needed. This
    function keeps points unchanged and converts lines to their first point.
    """
    if geom is None or geom.is_empty:
        return None

    if geom.geom_type == "Point":
        return geom

    if isinstance(geom, LineString):
        return Point(geom.coords[0])

    if isinstance(geom, MultiLineString):
        first_line = list(geom.geoms)[0]
        return Point(first_line.coords[0])

    return geom.centroid


def bbox_from_wkt(
    wkt_polygon: str,
    source_crs: str = "EPSG:4326",
    target_crs: str = "EPSG:25832",
) -> tuple[float, float, float, float]:
    """Create a target-CRS bounding box from a WKT polygon.

    Parameters
    ----------
    wkt_polygon:
        Polygon in WKT format. By default, coordinates are assumed to be
        longitude/latitude in EPSG:4326.
    source_crs:
        Coordinate reference system of the WKT polygon.
    target_crs:
        Coordinate reference system required by the NRW WFS BBOX request.

    Returns
    -------
    tuple
        xmin, ymin, xmax, ymax in the target CRS.
    """
    geom = shapely_wkt.loads(wkt_polygon)
    area_gdf = gpd.GeoDataFrame(geometry=[geom], crs=source_crs).to_crs(target_crs)
    xmin, ymin, xmax, ymax = area_gdf.total_bounds
    return float(xmin), float(ymin), float(xmax), float(ymax)


def bbox_from_shapefile(
    shapefile_path: str | Path,
    target_crs: str = "EPSG:25832",
) -> tuple[float, float, float, float]:
    """Create a target-CRS bounding box from a shapefile or other vector file.

    Parameters
    ----------
    shapefile_path:
        Path to a shapefile or any vector format supported by GeoPandas.
    target_crs:
        Coordinate reference system required by the NRW WFS BBOX request.

    Returns
    -------
    tuple
        xmin, ymin, xmax, ymax in the target CRS.
    """
    shapefile_path = Path(shapefile_path)
    if not shapefile_path.exists():
        raise FileNotFoundError(f"Area file not found: {shapefile_path}")

    area_gdf = gpd.read_file(shapefile_path)
    if area_gdf.empty:
        raise ValueError(f"Area file contains no features: {shapefile_path}")

    if area_gdf.crs is None:
        raise ValueError(
            "Input area file has no CRS. Define the CRS before using it, "
            "for example with GeoDataFrame.set_crs(...)."
        )

    area_gdf = area_gdf.to_crs(target_crs)
    xmin, ymin, xmax, ymax = area_gdf.total_bounds
    return float(xmin), float(ymin), float(xmax), float(ymax)


def bbox_from_area_input(
    wkt_polygon: str | None = None,
    shapefile_path: str | Path | None = None,
    source_crs: str = "EPSG:4326",
    target_crs: str = "EPSG:25832",
) -> tuple[float, float, float, float]:
    """Create a target-CRS bounding box from either WKT or a vector file."""
    if bool(wkt_polygon) == bool(shapefile_path):
        raise ValueError("Provide exactly one area input: either WKT or shapefile_path.")

    if wkt_polygon:
        return bbox_from_wkt(wkt_polygon, source_crs=source_crs, target_crs=target_crs)

    return bbox_from_shapefile(shapefile_path, target_crs=target_crs)
