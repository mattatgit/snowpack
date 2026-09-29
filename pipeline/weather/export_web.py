from __future__ import annotations

import argparse
import json
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


def write_float32(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(np.asarray(array, dtype="<f4").tobytes(order="C"))


def run(
    forcing_root: Path,
    output_root: Path,
    target_resolution_m: float,
) -> None:
    metadata = json.loads((forcing_root / "forcing-meta.json").read_text(encoding="utf-8"))
    source_resolution = float(metadata["grid"]["resolution_m"])
    factor = max(1, int(round(target_resolution_m / source_resolution)))

    with np.load(forcing_root / "forcing-grid.npz") as data:
        elevation = block_mean(data["elevation_m"], factor)
        temperature = block_mean(data["temperature_c"], factor)
        precipitation = block_mean(data["precipitation_mm"], factor)
        snowfall = block_mean(data["snowfall_water_mm"], factor)
        wind_u = block_mean(data["wind_u_m_s"], factor)
        wind_v = block_mean(data["wind_v_m_s"], factor)
        shortwave = block_mean(data["shortwave_w_m2"], factor)

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
    transform = metadata["grid"]["transform"]
    source_height = int(metadata["grid"]["height"])
    source_width = int(metadata["grid"]["width"])
    height, width = elevation.shape
    used_source_height = height * factor
    used_source_width = width * factor
    cell_x = float(transform[0])
    cell_y = abs(float(transform[4]))
    west = float(transform[2])
    north = float(transform[5])
    east = west + used_source_width * cell_x
    south = north - used_source_height * cell_y

    web_meta = {
        "hours": int(temperature.shape[0]),
        "timestamps_end_jst": metadata["timestamps_end_jst"],
        "width": width,
        "height": height,
        "source_width": source_width,
        "source_height": source_height,
        "source_resolution_m": source_resolution,
        "render_resolution_m": source_resolution * factor,
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
    }
    (data_root / "weather-meta.json").write_text(
        json.dumps(web_meta, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Exported {temperature.shape[0]} weather hours on "
        f"{width} x {height} render grid at {source_resolution * factor:.1f} m"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export historical forcing for web viewer")
    parser.add_argument(
        "--forcing-root",
        type=Path,
        default=Path("data/processed/furanodake/weather/2025-12-29_2026-01-03"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("web"))
    parser.add_argument("--resolution", type=float, default=100.0)
    args = parser.parse_args()
    run(args.forcing_root, args.output_root, args.resolution)
