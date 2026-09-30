from __future__ import annotations

import argparse
import json
from pathlib import Path

import rasterio
from pyproj import Transformer


def run(
    terrain_root: Path,
    terrain_meta_path: Path,
    features_path: Path,
    output_path: Path,
) -> None:
    terrain_meta = json.loads(terrain_meta_path.read_text(encoding="utf-8"))
    features = json.loads(features_path.read_text(encoding="utf-8"))
    transformer = Transformer.from_crs("EPSG:4326", terrain_meta["crs"], always_xy=True)

    projected_points: list[tuple[float, float]] = []
    for feature in features:
        projected_points.append(
            transformer.transform(float(feature["lon"]), float(feature["lat"]))
        )

    with rasterio.open(terrain_root / "elevation.tif") as dataset:
        elevations = [
            float(sample[0]) for sample in dataset.sample(projected_points)
        ]

    output: list[dict] = []
    for feature, (x, y), elevation in zip(features, projected_points, elevations):
        item = dict(feature)
        item.update(
            {
                "x_m": float(x),
                "y_m": float(y),
                "elevation_m": elevation,
            }
        )
        output.append(item)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {len(output)} map features to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export labelled terrain features")
    parser.add_argument(
        "--terrain-root",
        type=Path,
        default=Path("data/processed/furanodake/terrain"),
    )
    parser.add_argument(
        "--terrain-meta",
        type=Path,
        default=Path("web/data/terrain-meta.json"),
    )
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("config/furanodake-features.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("web/data/features.json"),
    )
    args = parser.parse_args()
    run(args.terrain_root, args.terrain_meta, args.features, args.output)
