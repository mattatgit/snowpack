# Terrain pipeline

First target: build a reproducible Furanodake terrain grid.

Planned stages:

1. obtain best available GSI DEM for the selected extent;
2. mosaic/crop source tiles;
3. reproject into an appropriate projected CRS;
4. derive slope and aspect;
5. derive curvature/topographic position;
6. derive horizon / solar exposure;
7. derive wind-exposure features;
8. resample to the initial model grid;
9. export browser-ready terrain.

The first implementation should preserve the source DEM separately from all derived rasters.
