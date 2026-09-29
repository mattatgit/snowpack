from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling


def read_resampled(
    path: Path, resolution_m: float, resampling: Resampling
) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as dataset:
        source_resolution = abs(dataset.transform.a)
        scale = source_resolution / resolution_m
        width = max(2, int(round(dataset.width * scale)))
        height = max(2, int(round(dataset.height * scale)))
        array = dataset.read(
            1,
            out_shape=(height, width),
            resampling=resampling,
        ).astype(np.float32)
        meta = {
            "width": width,
            "height": height,
            "source_width": dataset.width,
            "source_height": dataset.height,
            "source_resolution_m": source_resolution,
            "resolution_m": resolution_m,
            "crs": dataset.crs.to_string(),
            "west_m": dataset.bounds.left,
            "south_m": dataset.bounds.bottom,
            "east_m": dataset.bounds.right,
            "north_m": dataset.bounds.top,
        }
    return array, meta


def write_float32(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    little_endian = np.asarray(array, dtype="<f4")
    path.write_bytes(little_endian.tobytes(order="C"))


def run(terrain_root: Path, output_root: Path, resolution_m: float) -> None:
    elevation, meta = read_resampled(
        terrain_root / "elevation.tif", resolution_m, Resampling.bilinear
    )
    slope, _ = read_resampled(
        terrain_root / "slope-degrees.tif", resolution_m, Resampling.bilinear
    )
    aspect, _ = read_resampled(
        terrain_root / "aspect-degrees.tif", resolution_m, Resampling.nearest
    )

    if not np.all(np.isfinite(elevation)):
        raise ValueError("web export requires a complete elevation surface")

    write_float32(output_root / "data" / "elevation.bin", elevation)
    write_float32(output_root / "data" / "slope.bin", slope)
    write_float32(output_root / "data" / "aspect.bin", aspect)

    terrain_metadata = json.loads(
        (terrain_root / "metadata.json").read_text(encoding="utf-8")
    )
    meta.update(
        {
            "elevation_min_m": float(np.nanmin(elevation)),
            "elevation_max_m": float(np.nanmax(elevation)),
            "slope_min_deg": float(np.nanmin(slope)),
            "slope_max_deg": float(np.nanmax(slope)),
            "source_attribution": terrain_metadata["attribution"],
            "study": terrain_metadata["config"],
        }
    )
    (output_root / "data" / "terrain-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Exported {meta['width']} x {meta['height']} web grid "
        f"at {resolution_m:g} m to {output_root}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Furanodake terrain for the Three.js viewer"
    )
    parser.add_argument(
        "--terrain-root",
        type=Path,
        default=Path("data/processed/furanodake/terrain"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("web"))
    parser.add_argument("--resolution", type=float, default=20.0)
    args = parser.parse_args()
    run(args.terrain_root, args.output_root, args.resolution)
