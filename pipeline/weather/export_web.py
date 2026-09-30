from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def block_mean(array: np.ndarray, factor: int) -> np.ndarray:
    if factor <= 1:
        return array.astype(np.float32, copy=False)
    if array.ndim == 2:
        height = array.shape[0] // factor * factor
        width = array.shape[1] // factor * factor
        work = array[:height, :width]
        return work.reshape(height // factor, factor, width // factor, factor).mean(
            axis=(1, 3)
        ).astype(np.float32)
    if array.ndim == 3:
        hours = array.shape[0]
        height = array.shape[1] // factor * factor
        width = array.shape[2] // factor * factor
        work = array[:, :height, :width]
        return work.reshape(
            hours, height // factor, factor, width // factor, factor
        ).mean(axis=(2, 4)).astype(np.float32)
    raise ValueError("block_mean supports 2D or 3D arrays")


def crop_slices(
    transform: list[float],
    width: int,
    height: int,
    bounds: dict[str, float],
) -> tuple[slice, slice, dict[str, float]]:
    cell_x = float(transform[0])
    cell_y = abs(float(transform[4]))
    origin_x = float(transform[2])
    origin_y = float(transform[5])

    col0 = max(0, int(math.floor((bounds["west"] - origin_x) / cell_x)))
    col1 = min(width, int(math.ceil((bounds["east"] - origin_x) / cell_x)))
    row0 = max(0, int(math.floor((origin_y - bounds["north"]) / cell_y)))
    row1 = min(height, int(math.ceil((origin_y - bounds["south"]) / cell_y)))

    if col1 <= col0 or row1 <= row0:
        raise ValueError("viewer bounds do not intersect forcing grid")

    actual = {
        "west": origin_x + col0 * cell_x,
        "east": origin_x + col1 * cell_x,
        "north": origin_y - row0 * cell_y,
        "south": origin_y - row1 * cell_y,
    }
    return slice(row0, row1), slice(col0, col1), actual


def write_float32(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(np.asarray(array, dtype="<f4").tobytes(order="C"))


def run(
    forcing_root: Path,
    output_root: Path,
    target_resolution_m: float,
) -> None:
    metadata = json.loads((forcing_root / "forcing-meta.json").read_text(encoding="utf-8"))
    terrain_meta = json.loads(
        (output_root / "data" / "terrain-meta.json").read_text(encoding="utf-8")
    )
    source_resolution = float(metadata["grid"]["resolution_m"])
    factor = max(1, int(round(target_resolution_m / source_resolution)))

    source_height = int(metadata["grid"]["height"])
    source_width = int(metadata["grid"]["width"])
    transform = metadata["grid"]["transform"]
    viewer_bounds = {
        "west": float(terrain_meta["west_m"]),
        "south": float(terrain_meta["south_m"]),
        "east": float(terrain_meta["east_m"]),
        "north": float(terrain_meta["north_m"]),
    }
    row_slice, col_slice, cropped_bounds = crop_slices(
        transform,
        source_width,
        source_height,
        viewer_bounds,
    )

    with np.load(forcing_root / "forcing-grid.npz") as data:
        elevation = block_mean(data["elevation_m"][row_slice, col_slice], factor)
        temperature = block_mean(
            data["temperature_c"][:, row_slice, col_slice], factor
        )
        precipitation = block_mean(
            data["precipitation_mm"][:, row_slice, col_slice], factor
        )
        snowfall = block_mean(
            data["snowfall_water_mm"][:, row_slice, col_slice], factor
        )
        wind_u = block_mean(data["wind_u_m_s"][:, row_slice, col_slice], factor)
        wind_v = block_mean(data["wind_v_m_s"][:, row_slice, col_slice], factor)
        shortwave = block_mean(
            data["shortwave_w_m2"][:, row_slice, col_slice], factor
        )

    wind_speed = np.hypot(wind_u, wind_v).astype(np.float32)
    wind_direction = (
        np.degrees(np.arctan2(-wind_u, -wind_v)) + 360.0
    ) % 360.0
    calm = wind_speed < 0.05
    wind_direction = wind_direction.astype(np.float32)
    wind_direction[calm] = np.nan

    data_root = output_root / "data"
    write_float32(data_root / "weather-elevation.bin", elevation)
    write_float32(data_root / "weather-temperature.bin", temperature)
    write_float32(data_root / "weather-precipitation.bin", precipitation)
    write_float32(data_root / "weather-snowfall-water.bin", snowfall)
    write_float32(data_root / "weather-wind-speed.bin", wind_speed)
    write_float32(data_root / "weather-wind-direction.bin", wind_direction)
    write_float32(data_root / "weather-shortwave.bin", shortwave)

    summary = pd.read_csv(forcing_root / "forcing-summary.csv")
    height, width = elevation.shape
    source_cell_x = float(transform[0])
    source_cell_y = abs(float(transform[4]))
    render_resolution_x = source_cell_x * factor
    render_resolution_y = source_cell_y * factor

    west = cropped_bounds["west"]
    north = cropped_bounds["north"]
    east = west + width * render_resolution_x
    south = north - height * render_resolution_y

    web_meta = {
        "hours": int(temperature.shape[0]),
        "timestamps_end_jst": metadata["timestamps_end_jst"],
        "width": width,
        "height": height,
        "source_width": source_width,
        "source_height": source_height,
        "source_resolution_m": source_resolution,
        "render_resolution_m": (render_resolution_x + render_resolution_y) / 2.0,
        "bounds_m": {
            "west": west,
            "south": south,
            "east": east,
            "north": north,
        },
        "summary": json.loads(summary.to_json(orient="records")),
        "model_warnings": {
            "wind": metadata["model"]["wind"]["warning"],
            "shortwave": metadata["model"]["shortwave"]["warning"],
        },
        "source": "JMA AMeDAS observations downscaled over GSI terrain",
        "cropped_to_viewer": True,
    }
    (data_root / "weather-meta.json").write_text(
        json.dumps(web_meta, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Exported {temperature.shape[0]} weather hours on focused "
        f"{width} x {height} render grid at ~{web_meta['render_resolution_m']:.1f} m"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export historical forcing for web viewer")
    parser.add_argument(
        "--forcing-root",
        type=Path,
        default=Path("data/processed/furanodake/weather/2025-12-29_2026-01-03"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("web"))
    parser.add_argument("--resolution", type=float, default=50.0)
    args = parser.parse_args()
    run(args.forcing_root, args.output_root, args.resolution)
