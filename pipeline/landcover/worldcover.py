from __future__ import annotations

import json
import math
import shutil
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject

WORLD_COVER_PREFIX = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map"
TREE_COVER_CLASS = 10


def worldcover_tile_name(lon: float, lat: float) -> str:
    lon_origin = math.floor(lon / 3.0) * 3
    lat_origin = math.floor(lat / 3.0) * 3
    ns = "N" if lat_origin >= 0 else "S"
    ew = "E" if lon_origin >= 0 else "W"
    return f"{ns}{abs(lat_origin):02d}{ew}{abs(lon_origin):03d}"


def download_worldcover_tile(tile: str, cache_root: Path) -> Path:
    filename = f"ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
    destination = cache_root / filename
    if destination.exists():
        return destination
    cache_root.mkdir(parents=True, exist_ok=True)
    url = f"{WORLD_COVER_PREFIX}/{filename}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "snowpack-poc/0.1 (+https://github.com/mattatgit/snowpack)"},
    )
    tmp = destination.with_suffix(".tif.part")
    with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as output:
        shutil.copyfileobj(response, output)
    tmp.replace(destination)
    return destination


def export_forest_mask(
    terrain_meta_path: Path,
    output_root: Path,
    cache_root: Path,
) -> dict:
    terrain_meta = json.loads(terrain_meta_path.read_text(encoding="utf-8"))
    study = terrain_meta["study"]
    bbox = study["acquisition_bbox_wgs84"]
    centre_lon = (bbox[0] + bbox[2]) / 2.0
    centre_lat = (bbox[1] + bbox[3]) / 2.0
    tile = worldcover_tile_name(centre_lon, centre_lat)
    source_path = download_worldcover_tile(tile, cache_root)

    width = int(terrain_meta["width"])
    height = int(terrain_meta["height"])
    west = float(terrain_meta["west_m"])
    south = float(terrain_meta["south_m"])
    east = float(terrain_meta["east_m"])
    north = float(terrain_meta["north_m"])
    target_transform = from_bounds(west, south, east, north, width, height)

    classes = np.zeros((height, width), dtype=np.uint8)
    with rasterio.open(source_path) as source:
        reproject(
            source=rasterio.band(source, 1),
            destination=classes,
            src_transform=source.transform,
            src_crs=source.crs,
            dst_transform=target_transform,
            dst_crs=terrain_meta["crs"],
            src_nodata=0,
            dst_nodata=0,
            resampling=Resampling.nearest,
        )

    forest = (classes == TREE_COVER_CLASS).astype(np.uint8)
    data_root = output_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    (data_root / "forest-mask.bin").write_bytes(forest.tobytes(order="C"))

    metadata = {
        "source": "ESA WorldCover 2021 v200",
        "source_tile": tile,
        "source_resolution_m": 10,
        "tree_cover_class": TREE_COVER_CLASS,
        "width": width,
        "height": height,
        "forest_cell_count": int(np.count_nonzero(forest)),
        "cell_count": int(forest.size),
        "forest_fraction": float(np.mean(forest)),
        "attribution": "© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium",
    }
    (data_root / "forest-meta.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return metadata


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export Furanodake forest mask for web viewer")
    parser.add_argument(
        "--terrain-meta",
        type=Path,
        default=Path("web/data/terrain-meta.json"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("web"))
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path("data/raw/worldcover"),
    )
    args = parser.parse_args()
    meta = export_forest_mask(args.terrain_meta, args.output_root, args.cache_root)
    print(
        f"Forest mask: {meta['forest_cell_count']:,}/{meta['cell_count']:,} "
        f"cells ({meta['forest_fraction']:.1%})"
    )
