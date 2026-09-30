from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.windows import Window, from_bounds


def projected_bbox(
    bbox_wgs84: list[float],
    target_crs: str,
) -> tuple[float, float, float, float]:
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
    return min(xs), min(ys), max(xs), max(ys)


def read_resampled(
    path: Path,
    resolution_m: float,
    resampling: Resampling,
    crop_bounds: tuple[float, float, float, float] | None,
) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as dataset:
        if crop_bounds is None:
            window = Window(0, 0, dataset.width, dataset.height)
        else:
            raw = from_bounds(*crop_bounds, transform=dataset.transform)
            window = raw.round_offsets().round_lengths()
            window = window.intersection(Window(0, 0, dataset.width, dataset.height))

        source_transform = dataset.window_transform(window)
        source_resolution = abs(source_transform.a)
        source_width = int(window.width)
        source_height = int(window.height)
        scale = source_resolution / resolution_m
        width = max(2, int(round(source_width * scale)))
        height = max(2, int(round(source_height * scale)))
        array = dataset.read(
            1,
            window=window,
            out_shape=(height, width),
            resampling=resampling,
        ).astype(np.float32)

        bounds = rasterio.windows.bounds(window, dataset.transform)
        meta = {
            "width": width,
            "height": height,
            "source_width": source_width,
            "source_height": source_height,
            "source_resolution_m": source_resolution,
            "resolution_m": resolution_m,
            "crs": dataset.crs.to_string(),
            "west_m": bounds[0],
            "south_m": bounds[1],
            "east_m": bounds[2],
            "north_m": bounds[3],
        }
    return array, meta


def write_float32(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    little_endian = np.asarray(array, dtype="<f4")
    path.write_bytes(little_endian.tobytes(order="C"))


def run(terrain_root: Path, output_root: Path, resolution_m: float) -> None:
    terrain_metadata = json.loads(
        (terrain_root / "metadata.json").read_text(encoding="utf-8")
    )
    config = terrain_metadata["config"]
    viewer_bbox = config.get("viewer_bbox_wgs84")
    crop_bounds = (
        projected_bbox(viewer_bbox, config["target_crs"])
        if viewer_bbox is not None
        else None
    )

    elevation, meta = read_resampled(
        terrain_root / "elevation.tif",
        resolution_m,
        Resampling.bilinear,
        crop_bounds,
    )
    slope, _ = read_resampled(
        terrain_root / "slope-degrees.tif",
        resolution_m,
        Resampling.bilinear,
        crop_bounds,
    )
    aspect, _ = read_resampled(
        terrain_root / "aspect-degrees.tif",
        resolution_m,
        Resampling.nearest,
        crop_bounds,
    )

    if not np.all(np.isfinite(elevation)):
        raise ValueError("web export requires a complete elevation surface")

    write_float32(output_root / "data" / "elevation.bin", elevation)
    write_float32(output_root / "data" / "slope.bin", slope)
    write_float32(output_root / "data" / "aspect.bin", aspect)

    meta.update(
        {
            "elevation_min_m": float(np.nanmin(elevation)),
            "elevation_max_m": float(np.nanmax(elevation)),
            "slope_min_deg": float(np.nanmin(slope)),
            "slope_max_deg": float(np.nanmax(slope)),
            "source_attribution": terrain_metadata["attribution"],
            "study": config,
            "viewer_bbox_wgs84": viewer_bbox,
        }
    )
    (output_root / "data" / "terrain-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Exported focused {meta['width']} x {meta['height']} web grid "
        f"at {resolution_m:g} m to {output_root}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export focused Furanodake terrain for the Three.js viewer"
    )
    parser.add_argument(
        "--terrain-root",
        type=Path,
        default=Path("data/processed/furanodake/terrain"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("web"))
    parser.add_argument("--resolution", type=float, default=10.0)
    args = parser.parse_args()
    run(args.terrain_root, args.output_root, args.resolution)
