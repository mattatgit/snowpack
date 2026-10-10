import math

import numpy as np

from pipeline.terrain.build_furanodake import terrain_derivatives
from pipeline.terrain.gsi import tile_bounds_web_mercator, tile_range_for_bbox


def test_furanodake_dem5_tile_range():
    tiles = tile_range_for_bbox((142.58, 43.35, 142.70, 43.44), 15)
    assert (tiles.xmin, tiles.xmax) == (29361, 29372)
    assert (tiles.ymin, tiles.ymax) == (11985, 11996)
    assert tiles.count == 144


def test_furanodake_dem10_tile_range():
    tiles = tile_range_for_bbox((142.58, 43.35, 142.70, 43.44), 14)
    assert (tiles.xmin, tiles.xmax) == (14680, 14686)
    assert (tiles.ymin, tiles.ymax) == (5992, 5998)
    assert tiles.count == 49


def test_tile_bounds_have_positive_extent():
    left, bottom, right, top = tile_bounds_web_mercator(29366, 11991, 15)
    assert right > left
    assert top > bottom
    assert math.isclose(right - left, top - bottom, rel_tol=1e-12)


def test_slope_and_aspect_for_plane_rising_east():
    elevation = np.tile(np.arange(5, dtype=np.float32), (5, 1))
    slope, aspect = terrain_derivatives(elevation, resolution_m=1.0)
    assert np.allclose(slope, 45.0, atol=1e-4)
    assert np.allclose(aspect, 270.0, atol=1e-4)


def test_slope_and_aspect_for_plane_rising_north():
    elevation = np.tile(np.arange(4, -1, -1, dtype=np.float32)[:, None], (1, 5))
    slope, aspect = terrain_derivatives(elevation, resolution_m=1.0)
    assert np.allclose(slope, 45.0, atol=1e-4)
    assert np.allclose(aspect, 180.0, atol=1e-4)
