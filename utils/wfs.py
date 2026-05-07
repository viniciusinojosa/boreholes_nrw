"""Functions for requesting and parsing NRW BoreholeML/WFS data."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests

from .geometry import bbox_from_area_input, force_point_geometry

BMLH_BASE_URL = "https://www.bml3.nrw.de/service/bmlh"
BML_BASE_URL = "https://www.bml3.nrw.de/service/bml"


def get_text(parent, path: str, ns: dict[str, str]) -> Optional[str]:
    """Safely extract stripped text from an XML element."""
    elem = parent.find(path, ns)
    if elem is None or elem.text is None:
        return None
    return elem.text.strip()


def download_borehole_headers(
    wkt_polygon: str | None = None,
    output_gml: Path = Path("borehole_headers.gml"),
    source_crs: str = "EPSG:4326",
    target_crs: str = "EPSG:25832",
    shapefile_path: str | Path | None = None,
) -> gpd.GeoDataFrame:
    """Download borehole header features inside an area-derived bounding box.

    The area can be provided either as a WKT polygon or as a shapefile/vector
    file path. The NRW WFS request is made with a BBOX calculated after
    reprojection to EPSG:25832.
    """
    xmin, ymin, xmax, ymax = bbox_from_area_input(
        wkt_polygon=wkt_polygon,
        shapefile_path=shapefile_path,
        source_crs=source_crs,
        target_crs=target_crs,
    )

    params = {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": "bmlh:BoreholeHeader",
        "SRSNAME": target_crs,
        "BBOX": f"{xmin},{ymin},{xmax},{ymax},{target_crs}",
    }

    response = requests.get(BMLH_BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    output_gml.write_bytes(response.content)

    gdf = gpd.read_file(output_gml)
    gdf["geometry"] = gdf.geometry.apply(force_point_geometry)

    return gpd.GeoDataFrame(gdf, geometry="geometry", crs=gdf.crs)

def parse_borehole_layers(feature_id: str) -> pd.DataFrame:
    """Download and parse stratigraphic/lithological layers for one borehole."""
    params = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "VERSION": "1.1.0",
        "TYPENAME": "Borehole",
        "featureID": feature_id,
        "outputFormat": "text/xml",
    }

    response = requests.get(BML_BASE_URL, params=params, timeout=90)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    ns = {
        "bml": "http://www.infogeo.de/boreholeml/3.0",
        "gmd": "http://www.isotc211.org/2005/gmd",
    }

    rows = []
    for layer in root.findall(".//bml:layer", ns):
        rows.append(
            {
                "feature_id": feature_id,
                "from_m": get_text(layer, ".//bml:from", ns),
                "to_m": get_text(layer, ".//bml:to", ns),
                "rock_code": get_text(layer, ".//bml:rockCode", ns),
                "rock_name": get_text(
                    layer,
                    ".//bml:rockNameText/gmd:LocalisedCharacterString",
                    ns,
                ),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        for col in ["from_m", "to_m"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["from_m", "to_m"])

    return df


def download_all_layers(borehole_ids: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Download stratigraphy for multiple boreholes.

    Returns
    -------
    tuple
        Combined layer table and list of skipped/failed borehole IDs.
    """
    dfs = []
    failed_ids = []

    for feature_id in borehole_ids:
        try:
            df = parse_borehole_layers(feature_id)
            if df.empty:
                failed_ids.append(feature_id)
            else:
                dfs.append(df)
        except Exception as exc:
            print(f"Skipped {feature_id}: {exc}")
            failed_ids.append(feature_id)

    all_layers = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    return all_layers, failed_ids
