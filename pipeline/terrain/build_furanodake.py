from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.warp import reproject

from pipeline.terrain.gsi import (
    GSI_DEM10_SOURCE,
    GSI_DEM5_SOURCES,
    build_tile_mosaic,
    mosaic_transform,
    tile_range_for_bbox,
    write_tile_manifest,
)


def destination_grid(
    bbox_wgs84: tuple[float, float, float, float], target_crs: str, resolution_m: float
) -> tuple[Affine, int, int]:
    """Create a target grid aligned to whole resolution increments in the projected CRS."""
    west, south, east, north = bbox_wgs84
    transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
    corners = [
        transformer.transform(west, south),
        transformer.transform(west, north),
        transformer.transform(east, south),
        transformer.transform(east, north),
    ]
    xs = [point[0] for point in corners]
    ys = [point[1] for point in corners]
    left = math.floor(min(xs) / resolution_m) * resolution_m
    right = math.ceil(max(xs) / resolution_m) * resolution_m
    bottom = math.floor(min(ys) / resolution_m) * resolution_m
    top = math.ceil(max(ys) / resolution_m) * resolution_m
    width = int(round((right - left) / resolution_m))
    height = int(round((top - bottom) / resolution_m))
    return Affine(resolution_m, 0.0, left, 0.0, -resolution_m, top), width, height


def reproject_array(
    source: np.ndarray,
    source_transform: Affine,
    destination_transform: Affine,
    width: int,
    height: int,
    target_crs: str,
    resampling: Resampling,
    source_nodata: float | int,
    destination_nodata: float | int,
    dtype: np.dtype,
) -> np.ndarray:
    destination = np.full((height, width), destination_nodata, dtype=dtype)
    reproject(
        source=source,
        destination=destination,
        src_transform=source_transform,
        src_crs="EPSG:3857",
        src_nodata=source_nodata,
        dst_transform=destination_transform,
        dst_crs=target_crs,
        dst_nodata=destination_nodata,
        resampling=resampling,
    )
    return destination


def terrain_derivatives(
    elevation: np.ndarray, resolution_m: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return slope degrees and downslope aspect degrees clockwise from north."""
    valid = np.isfinite(elevation)
    if not np.any(valid):
        return (
            np.full_like(elevation, np.nan, dtype=np.float32),
            np.full_like(elevation, np.nan, dtype=np.float32),
        )

    fill_value = float(np.nanmedian(elevation))
    work = np.where(valid, elevation, fill_value).astype(np.float64)
    dz_dnorth, dz_deast = np.gradient(work, -resolution_m, resolution_m)
    slope = np.degrees(np.arctan(np.hypot(dz_deast, dz_dnorth))).astype(np.float32)
    aspect = (np.degrees(np.arctan2(-dz_deast, -dz_dnorth)) + 360.0) % 360.0
    aspect = aspect.astype(np.float32)

    slope[~valid] = np.nan
    aspect[~valid] = np.nan
    aspect[slope < 0.05] = np.nan
    return slope, aspect


def write_geotiff(
    path: Path,
    array: np.ndarray,
    transform: Affine,
    crs: str,
    dtype: str,
    nodata: float | int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": array.shape[0],
        "width": array.shape[1],
        "count": 1,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "compress": "deflate",
        "predictor": 3 if dtype.startswith("float") else 2,
        "tiled": True,
    }
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(array.astype(dtype), 1)


def run(config_path: Path, data_root: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    bbox = tuple(float(value) for value in config["acquisition_bbox_wgs84"])
    target_crs = str(config["target_crs"])
    resolution_m = float(config["target_resolution_m"])
    dem5_zoom = int(config["dem5_zoom"])
    dem10_zoom = int(config["dem10_zoom"])

    raw_root = data_root / "raw" / "gsi"
    output_root = data_root / "processed" / config["name"] / "terrain"
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = write_tile_manifest(output_root / "gsi-tile-manifest.json", bbox)

    dem5_range = tile_range_for_bbox(bbox, dem5_zoom)
    dem5, dem5_source, dem5_counts = build_tile_mosaic(
        raw_root, dem5_range, GSI_DEM5_SOURCES
    )

    dem10_range = tile_range_for_bbox(bbox, dem10_zoom)
    dem10, _, dem10_counts = build_tile_mosaic(
        raw_root, dem10_range, (GSI_DEM10_SOURCE,)
    )

    dst_transform, width, height = destination_grid(bbox, target_crs, resolution_m)
    high = reproject_array(
        dem5,
        mosaic_transform(dem5_range),
        dst_transform,
        width,
        height,
        target_crs,
        Resampling.bilinear,
        np.nan,
        np.nan,
        np.dtype("float32"),
    )
    fallback = reproject_array(
        dem10,
        mosaic_transform(dem10_range),
        dst_transform,
        width,
        height,
        target_crs,
        Resampling.bilinear,
        np.nan,
        np.nan,
        np.dtype("float32"),
    )
    source_quality = reproject_array(
        dem5_source,
        mosaic_transform(dem5_range),
        dst_transform,
        width,
        height,
        target_crs,
        Resampling.nearest,
        0,
        0,
        np.dtype("uint8"),
    )

    fallback_cells = ~np.isfinite(high) & np.isfinite(fallback)
    elevation = high.copy()
    elevation[fallback_cells] = fallback[fallback_cells]
    source_quality[fallback_cells] = 4

    slope, aspect = terrain_derivatives(elevation, resolution_m)

    write_geotiff(
        output_root / "elevation.tif",
        elevation,
        dst_transform,
        target_crs,
        "float32",
        np.nan,
    )
    write_geotiff(
        output_root / "slope-degrees.tif",
        slope,
        dst_transform,
        target_crs,
        "float32",
        np.nan,
    )
    write_geotiff(
        output_root / "aspect-degrees.tif",
        aspect,
        dst_transform,
        target_crs,
        "float32",
        np.nan,
    )
    write_geotiff(
        output_root / "source-quality.tif",
        source_quality,
        dst_transform,
        target_crs,
        "uint8",
        0,
    )

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "tile_manifest": manifest,
        "tile_download_counts": {"dem5": dem5_counts, "dem10": dem10_counts},
        "output_grid": {
            "crs": target_crs,
            "resolution_m": resolution_m,
            "width": width,
            "height": height,
            "transform": list(dst_transform)[:6],
        },
        "source_quality_codes": {
            "0": "nodata",
            "1": "GSI DEM5A",
            "2": "GSI DEM5B",
            "3": "GSI DEM5C",
            "4": "GSI DEM10B fallback",
        },
        "attribution": "地理院タイル（標高タイル（基盤地図情報数値標高モデル））を加工して作成",
    }
    (output_root / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    valid_count = int(np.count_nonzero(np.isfinite(elevation)))
    total_count = int(elevation.size)
    print(f"Wrote {output_root}")
    print(
        f"Valid elevation cells: {valid_count:,}/{total_count:,} "
        f"({valid_count / total_count:.1%})"
    )
    print(f"DEM5 tile counts: {dem5_counts}")
    print(f"DEM10 tile counts: {dem10_counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build the Furanodake terrain dataset from GSI DEM tiles"
    )
    parser.add_argument(
        "--config", type=Path, default=Path("config/furanodake.json")
    )
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    args = parser.parse_args()
    run(args.config, args.data_root)
