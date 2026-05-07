"""Command-line workflow for NRW borehole stratigraphy retrieval and 3D plotting.

Examples
--------
Using a WKT polygon in EPSG:4326:

python borehole_3d.py ^
  --wkt "POLYGON ((7.210851 51.486534, 7.217041 51.486534, 7.217041 51.488618, 7.210851 51.488618, 7.210851 51.486534))" ^
  --step 0.1 ^
  --color-column rock_name ^
  --output-gpkg borehole_layers_3d.gpkg ^
  --output-html boreholes_3d.html

Using a shapefile/vector file:
python borehole_3d.py ^
  --shapefile-path "aoi_2.shp" ^
  --step 0.1 ^
  --color-column rock_name ^
  --output-gpkg borehole_layers_3d.gpkg ^
  --output-html boreholes_3d.html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from utils import (
    build_3d_geodataframe,
    create_3d_plot,
    download_all_layers,
    download_borehole_headers,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download NRW BoreholeML data and create a 3D stratigraphy plot."
    )

    area_group = parser.add_mutually_exclusive_group(required=True)
    area_group.add_argument(
        "--wkt",
        help="Input polygon WKT. Default CRS is EPSG:4326 longitude/latitude.",
    )
    area_group.add_argument(
        "--shapefile-path",
        help="Path to an AOI shapefile or other vector file supported by GeoPandas.",
    )

    parser.add_argument(
        "--wkt-crs",
        default="EPSG:4326",
        help="CRS of the input WKT polygon. Default: EPSG:4326.",
    )
    parser.add_argument(
        "--target-crs",
        default="EPSG:25832",
        help="CRS used for the NRW WFS BBOX request. Default: EPSG:25832.",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=0.1,
        help="Depth grid step in metres. Default: 0.1 m.",
    )
    parser.add_argument(
        "--color-column",
        default="rock_name",
        help="Column used for colouring the 3D plot. Default: rock_name.",
    )
    parser.add_argument(
        "--output-gml",
        default="borehole_headers.gml",
        help="Output path for downloaded GML borehole headers.",
    )
    parser.add_argument(
        "--output-gpkg",
        default="borehole_layers_3d.gpkg",
        help="Output path for processed GeoPackage.",
    )
    parser.add_argument(
        "--output-html",
        default="boreholes_3d.html",
        help="Output path for Plotly HTML plot.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the complete borehole stratigraphy workflow."""
    args = parse_args()

    headers_gdf = download_borehole_headers(
        wkt_polygon=args.wkt,
        shapefile_path=args.shapefile_path,
        output_gml=Path(args.output_gml),
        source_crs=args.wkt_crs,
        target_crs=args.target_crs,
    )
    print(f"Downloaded borehole headers: {len(headers_gdf)}")

    if "id" not in headers_gdf.columns:
        raise KeyError(
            "The downloaded borehole header layer does not contain an 'id' column. "
            "Check the WFS response or service schema."
        )

    borehole_ids = headers_gdf["id"].astype(str).to_list()
    layers_df, failed_ids = download_all_layers(borehole_ids)

    parsed_count = layers_df["feature_id"].nunique() if not layers_df.empty else 0
    print(f"Parsed boreholes with stratigraphy: {parsed_count}")
    print(f"Skipped/failed borehole IDs: {len(failed_ids)}")

    if layers_df.empty:
        raise RuntimeError(
            "No stratigraphy layers were parsed. Check the area input or WFS response."
        )

    gdf3d = build_3d_geodataframe(headers_gdf, layers_df, step=args.step)
    gdf3d.to_file(args.output_gpkg, driver="GPKG")
    print(f"Saved processed GeoPackage: {args.output_gpkg}")

    fig = create_3d_plot(gdf3d, color_column=args.color_column)
    fig.write_html(args.output_html, auto_open=False)
    print(f"Saved 3D plot: {args.output_html}")


if __name__ == "__main__":
    main()
