from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from pathlib import Path

GSI_URL = "https://cyberjapandata.gsi.go.jp/xyz/dem1a_png/{z}/{x}/{y}.png"


def lonlat_to_tile(lon: float, lat: float, zoom: int) -> tuple[int, int]:
    n = 2**zoom
    x = int(math.floor((lon + 180.0) / 360.0 * n))
    lat_rad = math.radians(lat)
    y = int(
        math.floor(
            (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        )
    )
    return x, y


def available(lon: float, lat: float, zoom: int = 17) -> dict:
    x, y = lonlat_to_tile(lon, lat, zoom)
    url = GSI_URL.format(z=zoom, x=x, y=y)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "snowpack-poc/0.1 (+https://github.com/mattatgit/snowpack)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(64)
            ok = response.status == 200 and payload.startswith(b"\x89PNG")
            status = response.status
    except urllib.error.HTTPError as exc:
        ok = False
        status = exc.code
    return {"lon": lon, "lat": lat, "z": zoom, "x": x, "y": y, "url": url, "status": status, "available": ok}


def run(config_path: Path) -> list[dict]:
    config = json.loads(config_path.read_text())
    west, south, east, north = config["acquisition_bbox_wgs84"]
    samples = [
        ("centre", (west + east) / 2.0, (south + north) / 2.0),
        ("northwest", west + 0.01, north - 0.01),
        ("northeast", east - 0.01, north - 0.01),
        ("southwest", west + 0.01, south + 0.01),
        ("southeast", east - 0.01, south + 0.01),
        ("furanodake", 142.635, 43.393611),
    ]
    results = []
    for name, lon, lat in samples:
        item = available(lon, lat)
        item["name"] = name
        results.append(item)
        print(f"{name:12s} DEM1A {'YES' if item['available'] else 'NO '} HTTP {item['status']} tile {item['x']}/{item['y']}")
    return results


if __name__ == "__main__":
    run(Path("config/furanodake.json"))
