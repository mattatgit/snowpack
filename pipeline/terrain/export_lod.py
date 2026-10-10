from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


DATA_ROOT = Path("web/data")
LOD_ROOT = DATA_ROOT / "lod"


def read_float32(path: Path, width: int, height: int) -> np.ndarray:
    data = np.fromfile(path, dtype="<f4")
    expected = width * height
    if data.size != expected:
        raise ValueError(f"{path} contains {data.size} values; expected {expected}")
    return data.reshape((height, width))


def write_float32(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.asarray(array, dtype="<f4").tofile(path)


def resample_bilinear(array: np.ndarray, width: int, height: int) -> np.ndarray:
    """Small dependency-free bilinear resampler for the browser fallback mesh."""
    src_h, src_w = array.shape
    xs = np.linspace(0.0, src_w - 1, width, dtype=np.float64)
    ys = np.linspace(0.0, src_h - 1, height, dtype=np.float64)

    x0 = np.floor(xs).astype(np.int32)
    x1 = np.minimum(x0 + 1, src_w - 1)
    xf = (xs - x0).astype(np.float32)

    horizontal = np.empty((src_h, width), dtype=np.float32)
    for row in range(src_h):
        source = array[row]
        horizontal[row] = source[x0] * (1.0 - xf) + source[x1] * xf

    y0 = np.floor(ys).astype(np.int32)
    y1 = np.minimum(y0 + 1, src_h - 1)
    yf = (ys - y0).astype(np.float32)
    return horizontal[y0] * (1.0 - yf[:, None]) + horizontal[y1] * yf[:, None]


def run(
    data_root: Path = DATA_ROOT,
    tile_cells: int = 128,
    coarse_resolution_m: float = 20.0,
) -> None:
    meta = json.loads((data_root / "terrain-meta.json").read_text(encoding="utf-8"))
    width = int(meta["width"])
    height = int(meta["height"])
    source_resolution = float(meta["resolution_m"])
    if tile_cells < 16:
        raise ValueError("tile_cells must be at least 16")
    if coarse_resolution_m < source_resolution:
        raise ValueError("coarse resolution must not be finer than source terrain")

    elevation = read_float32(data_root / "elevation.bin", width, height)
    if not np.all(np.isfinite(elevation)):
        raise ValueError("LOD export requires finite terrain elevations")

    span_x = float(meta["east_m"] - meta["west_m"])
    span_z = float(meta["north_m"] - meta["south_m"])

    coarse_width = max(
        2,
        int(round((width - 1) * source_resolution / coarse_resolution_m)) + 1,
    )
    coarse_height = max(
        2,
        int(round((height - 1) * source_resolution / coarse_resolution_m)) + 1,
    )
    coarse = resample_bilinear(elevation, coarse_width, coarse_height)

    lod_root = data_root / "lod"
    write_float32(lod_root / "coarse-20m.bin", coarse)

    tiles: list[dict] = []
    tile_rows = math.ceil((height - 1) / tile_cells)
    tile_cols = math.ceil((width - 1) / tile_cells)

    for tile_row in range(tile_rows):
        row0 = tile_row * tile_cells
        row1 = min(height - 1, row0 + tile_cells)
        for tile_col in range(tile_cols):
            col0 = tile_col * tile_cells
            col1 = min(width - 1, col0 + tile_cells)
            tile = elevation[row0 : row1 + 1, col0 : col1 + 1]
            tile_id = f"r{tile_row}-c{tile_col}"
            relative_path = f"./data/lod/5m/{tile_id}.bin"
            write_float32(lod_root / "5m" / f"{tile_id}.bin", tile)

            u0 = col0 / (width - 1)
            u1 = col1 / (width - 1)
            v0 = row0 / (height - 1)
            v1 = row1 / (height - 1)
            x0 = (u0 - 0.5) * span_x
            x1 = (u1 - 0.5) * span_x
            z0 = (v0 - 0.5) * span_z
            z1 = (v1 - 0.5) * span_z

            tiles.append(
                {
                    "id": tile_id,
                    "row": tile_row,
                    "col": tile_col,
                    "row0": row0,
                    "row1": row1,
                    "col0": col0,
                    "col1": col1,
                    "width": int(tile.shape[1]),
                    "height": int(tile.shape[0]),
                    "path": relative_path,
                    "u0": u0,
                    "u1": u1,
                    "v0": v0,
                    "v1": v1,
                    "x0_m": x0,
                    "x1_m": x1,
                    "z0_m": z0,
                    "z1_m": z1,
                    "centre_x_m": (x0 + x1) / 2.0,
                    "centre_z_m": (z0 + z1) / 2.0,
                }
            )

    lod_meta = {
        "version": 1,
        "source_resolution_m": source_resolution,
        "source_width": width,
        "source_height": height,
        "tile_cells": tile_cells,
        "tile_rows": tile_rows,
        "tile_cols": tile_cols,
        "coarse": {
            "resolution_m": coarse_resolution_m,
            "width": coarse_width,
            "height": coarse_height,
            "path": "./data/lod/coarse-20m.bin",
        },
        "tiles": tiles,
    }
    (lod_root / "lod-meta.json").write_text(
        json.dumps(lod_meta, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    tile_mib = sum((tile["width"] * tile["height"] * 4) for tile in tiles) / 2**20
    coarse_kib = coarse.size * 4 / 1024
    print(
        f"Exported terrain LOD: {coarse_width}x{coarse_height} coarse "
        f"({coarse_kib:.0f} KiB) + {len(tiles)} 5 m tiles ({tile_mib:.1f} MiB total)"
    )


if __name__ == "__main__":
    run()
