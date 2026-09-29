from __future__ import annotations

import json
import math
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
from rasterio.transform import Affine

WEB_MERCATOR_HALF_WORLD_M = 20037508.342789244
TILE_SIZE_PX = 256
GSI_BASE_URL = "https://cyberjapandata.gsi.go.jp/xyz"
GSI_DEM5_SOURCES = ("dem5a_png", "dem5b_png", "dem5c_png")
GSI_DEM10_SOURCE = "dem_png"


@dataclass(frozen=True)
class TileRange:
    zoom: int
    xmin: int
    xmax: int
    ymin: int
    ymax: int

    @property
    def columns(self) -> int:
        return self.xmax - self.xmin + 1

    @property
    def rows(self) -> int:
        return self.ymax - self.ymin + 1

    @property
    def count(self) -> int:
        return self.columns * self.rows

    def tiles(self) -> Iterable[tuple[int, int]]:
        for y in range(self.ymin, self.ymax + 1):
            for x in range(self.xmin, self.xmax + 1):
                yield x, y


def lonlat_to_tile_fraction(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    """Convert WGS84 lon/lat to fractional XYZ tile coordinates."""
    if not -180.0 <= lon <= 180.0:
        raise ValueError("longitude must be between -180 and 180 degrees")
    lat = max(min(lat, 85.05112878), -85.05112878)
    n = 2**zoom
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def tile_range_for_bbox(bbox: tuple[float, float, float, float], zoom: int) -> TileRange:
    """Return inclusive XYZ tiles covering west,south,east,north WGS84 bbox."""
    west, south, east, north = bbox
    if west >= east or south >= north:
        raise ValueError("bbox must be west,south,east,north")
    xw, ys = lonlat_to_tile_fraction(west, south, zoom)
    xe, yn = lonlat_to_tile_fraction(east, north, zoom)
    return TileRange(
        zoom=zoom,
        xmin=math.floor(xw),
        xmax=math.floor(xe),
        ymin=math.floor(yn),
        ymax=math.floor(ys),
    )


def tile_bounds_web_mercator(x: int, y: int, zoom: int) -> tuple[float, float, float, float]:
    """Return left,bottom,right,top bounds for an XYZ tile in EPSG:3857 metres."""
    world_m = WEB_MERCATOR_HALF_WORLD_M * 2.0
    tile_span = world_m / (2**zoom)
    left = -WEB_MERCATOR_HALF_WORLD_M + x * tile_span
    right = left + tile_span
    top = WEB_MERCATOR_HALF_WORLD_M - y * tile_span
    bottom = top - tile_span
    return left, bottom, right, top


def mosaic_transform(tile_range: TileRange) -> Affine:
    """Affine transform for a 256px XYZ tile mosaic in EPSG:3857."""
    left, _, _, top = tile_bounds_web_mercator(
        tile_range.xmin, tile_range.ymin, tile_range.zoom
    )
    world_m = WEB_MERCATOR_HALF_WORLD_M * 2.0
    pixel_size = world_m / (2**tile_range.zoom) / TILE_SIZE_PX
    return Affine(pixel_size, 0.0, left, 0.0, -pixel_size, top)


def gsi_tile_url(source: str, zoom: int, x: int, y: int) -> str:
    return f"{GSI_BASE_URL}/{source}/{zoom}/{x}/{y}.png"


def decode_gsi_elevation_png(path: Path) -> np.ndarray:
    """Decode a GSI 24-bit PNG elevation tile into float32 metres with NaN nodata."""
    with rasterio.open(path) as dataset:
        rgb = dataset.read((1, 2, 3)).astype(np.int32)
    packed = (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]
    elevation = np.empty(packed.shape, dtype=np.float32)
    nodata = packed == 2**23
    positive = packed < 2**23
    elevation[positive] = packed[positive] * 0.01
    negative = ~(positive | nodata)
    elevation[negative] = (packed[negative] - 2**24) * 0.01
    elevation[nodata] = np.nan
    return elevation


def _download(url: str, destination: Path, timeout_s: int = 30) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "snowpack-poc/0.1 (+https://github.com/mattatgit/snowpack)"},
    )
    tmp = destination.with_suffix(destination.suffix + ".part")
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response, tmp.open("wb") as fh:
            if getattr(response, "status", 200) != 200:
                return False
            shutil.copyfileobj(response, fh)
        tmp.replace(destination)
        return True
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 404):
            tmp.unlink(missing_ok=True)
            return False
        raise
    finally:
        tmp.unlink(missing_ok=True)


def acquire_tile(
    cache_root: Path,
    sources: tuple[str, ...],
    zoom: int,
    x: int,
    y: int,
) -> tuple[Path | None, str | None]:
    """Acquire first available source for one tile, respecting source priority."""
    for source in sources:
        path = cache_root / source / str(zoom) / str(x) / f"{y}.png"
        if path.exists() or _download(gsi_tile_url(source, zoom, x, y), path):
            return path, source
    return None, None


def build_tile_mosaic(
    cache_root: Path,
    tile_range: TileRange,
    sources: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Build elevation and source-code mosaics from prioritized GSI sources."""
    height = tile_range.rows * TILE_SIZE_PX
    width = tile_range.columns * TILE_SIZE_PX
    elevation = np.full((height, width), np.nan, dtype=np.float32)
    source_code = np.zeros((height, width), dtype=np.uint8)
    source_ids = {source: index + 1 for index, source in enumerate(sources)}
    counts = {source: 0 for source in sources}
    counts["missing"] = 0

    for x, y in tile_range.tiles():
        path, source = acquire_tile(cache_root, sources, tile_range.zoom, x, y)
        row = (y - tile_range.ymin) * TILE_SIZE_PX
        col = (x - tile_range.xmin) * TILE_SIZE_PX
        if path is None or source is None:
            counts["missing"] += 1
            continue
        tile = decode_gsi_elevation_png(path)
        elevation[row : row + TILE_SIZE_PX, col : col + TILE_SIZE_PX] = tile
        source_code[row : row + TILE_SIZE_PX, col : col + TILE_SIZE_PX] = source_ids[source]
        counts[source] += 1

    return elevation, source_code, counts


def write_tile_manifest(path: Path, bbox: tuple[float, float, float, float]) -> dict:
    """Write deterministic tile ranges used by the Furanodake acquisition."""
    dem5 = tile_range_for_bbox(bbox, 15)
    dem10 = tile_range_for_bbox(bbox, 14)
    manifest = {
        "bbox_wgs84": list(bbox),
        "dem5": {
            "zoom": dem5.zoom,
            "sources_in_priority_order": list(GSI_DEM5_SOURCES),
            "xmin": dem5.xmin,
            "xmax": dem5.xmax,
            "ymin": dem5.ymin,
            "ymax": dem5.ymax,
            "tile_count": dem5.count,
        },
        "dem10_fallback": {
            "zoom": dem10.zoom,
            "source": GSI_DEM10_SOURCE,
            "xmin": dem10.xmin,
            "xmax": dem10.xmax,
            "ymin": dem10.ymin,
            "ymax": dem10.ymax,
            "tile_count": dem10.count,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
