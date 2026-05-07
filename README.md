# Boreholes Information from Geologischer Dienst Nordrhein-Westfalen

## Overview
This script retrieves borehole information from the public NRW borehole database (https://www.bohrungen.nrw.de/) for a user-defined area of interest. The area is provided as a WKT polygon, which is converted into a spatial bounding box and used to request borehole data from the NRW BoreholeML/WFS service.

The script downloads borehole header information and extracts the associated stratigraphic/lithological layers for each borehole. These layers are then processed into a structured geospatial dataset, including depth intervals, mid-depth values, lithological descriptions, and borehole coordinates.

Optionally, the stratigraphy can be discretized into regular depth intervals, for example 10 cm layers, allowing the borehole information to be visualized in three dimensions. The final output can be exported as geospatial files and as an interactive 3D Plotly HTML visualization.

## Main features

- Query borehole data from the NRW public borehole database
- Define the search area using a WKT polygon or with a shapefile 
- Retrieve borehole header and stratigraphy information
- Extract lithological descriptions and depth intervals
- Generate regular 10 cm subsurface layers (or with the interval prefered)
- Create an interactive 3D visualization of borehole stratigraphy
- Export processed data as geospatial files
