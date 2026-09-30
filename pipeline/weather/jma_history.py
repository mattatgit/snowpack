from __future__ import annotations

import io
import math
import re
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

JMA_HOURLY_URL = (
    "https://www.data.jma.go.jp/stats/etrn/view/hourly_a1.php"
    "?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day={day}&view="
)

WIND_DIRECTION_DEGREES = {
    "北": 0.0,
    "北北東": 22.5,
    "北東": 45.0,
    "東北東": 67.5,
    "東": 90.0,
    "東南東": 112.5,
    "南東": 135.0,
    "南南東": 157.5,
    "南": 180.0,
    "南南西": 202.5,
    "南西": 225.0,
    "西南西": 247.5,
    "西": 270.0,
    "西北西": 292.5,
    "北西": 315.0,
    "北北西": 337.5,
}


def flatten_column(column: object) -> str:
    if isinstance(column, tuple):
        parts: list[str] = []
        for value in column:
            text = str(value).strip()
            if not text or text.startswith("Unnamed:"):
                continue
            if not parts or parts[-1] != text:
                parts.append(text)
        return " / ".join(parts)
    return str(column).strip()


def numeric_value(value: object) -> float:
    if value is None:
        return math.nan
    text = str(value).strip()
    if not text or text in {"///", "--", "×", "nan"}:
        return math.nan
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not match:
        return math.nan
    return float(match.group(0))


def wind_direction_degrees(value: object) -> float:
    text = str(value).strip()
    if text in {"", "///", "--", "静穏", "nan"}:
        return math.nan
    return WIND_DIRECTION_DEGREES.get(text, math.nan)


def _find_column(columns: list[str], *needles: str, exclude: tuple[str, ...] = ()) -> str | None:
    for column in columns:
        if all(needle in column for needle in needles) and not any(
            value in column for value in exclude
        ):
            return column
    return None


def parse_hourly_table(html: bytes, observation_date: date, timezone: str) -> pd.DataFrame:
    tables = pd.read_html(io.BytesIO(html))
    candidates: list[pd.DataFrame] = []
    for table in tables:
        columns = [flatten_column(column) for column in table.columns]
        if any(column == "時" or column.startswith("時 /") for column in columns):
            candidates.append(table)

    if not candidates:
        raise ValueError("Could not find hourly observation table in JMA response")

    table = max(candidates, key=len).copy()
    table.columns = [flatten_column(column) for column in table.columns]
    columns = list(table.columns)

    hour_column = _find_column(columns, "時")
    precip_column = _find_column(columns, "降水量")
    temperature_column = _find_column(columns, "気温", exclude=("露点",))
    dewpoint_column = _find_column(columns, "露点")
    humidity_column = _find_column(columns, "湿度")
    wind_speed_column = _find_column(columns, "平均風速")
    wind_direction_column = _find_column(columns, "風向", exclude=("平均風速", "最大"))
    sunshine_column = _find_column(columns, "日照")
    snowfall_column = _find_column(columns, "降雪")
    snow_depth_column = _find_column(columns, "積雪")

    if hour_column is None:
        raise ValueError("JMA hourly table does not contain an hour column")

    tz = ZoneInfo(timezone)
    rows: list[dict[str, object]] = []
    for _, source in table.iterrows():
        hour = int(numeric_value(source[hour_column]))
        if not 1 <= hour <= 24:
            continue
        if hour == 24:
            end_time = datetime.combine(observation_date + timedelta(days=1), datetime.min.time(), tz)
        else:
            end_time = datetime(
                observation_date.year,
                observation_date.month,
                observation_date.day,
                hour,
                tzinfo=tz,
            )
        midpoint = end_time - timedelta(minutes=30)

        def number(column: str | None) -> float:
            return numeric_value(source[column]) if column is not None else math.nan

        wind_text = source[wind_direction_column] if wind_direction_column is not None else None
        rows.append(
            {
                "time_end_jst": end_time.isoformat(),
                "time_mid_jst": midpoint.isoformat(),
                "precipitation_mm": number(precip_column),
                "temperature_c": number(temperature_column),
                "dewpoint_c": number(dewpoint_column),
                "humidity_pct": number(humidity_column),
                "wind_speed_m_s": number(wind_speed_column),
                "wind_direction_deg": wind_direction_degrees(wind_text),
                "wind_direction_text": "" if wind_text is None else str(wind_text).strip(),
                "sunshine_hours": number(sunshine_column),
                "snowfall_cm": number(snowfall_column),
                "snow_depth_cm": number(snow_depth_column),
            }
        )

    result = pd.DataFrame(rows)
    if len(result) != 24:
        raise ValueError(f"Expected 24 hourly rows from JMA, got {len(result)}")
    return result


def fetch_hourly_day(
    prec_no: str,
    block_no: str,
    observation_date: date,
    timezone: str = "Asia/Tokyo",
    timeout_s: int = 30,
) -> pd.DataFrame:
    url = JMA_HOURLY_URL.format(
        prec_no=prec_no,
        block_no=block_no,
        year=observation_date.year,
        month=observation_date.month,
        day=observation_date.day,
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "snowpack-poc/0.1 (+https://github.com/mattatgit/snowpack)"},
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        html = response.read()
    frame = parse_hourly_table(html, observation_date, timezone)
    frame.insert(0, "source_url", url)
    return frame


def fetch_station_period(
    station: dict,
    start: datetime,
    end: datetime,
    timezone: str,
) -> pd.DataFrame:
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start/end must be timezone-aware")
    first_day = start.astimezone(ZoneInfo(timezone)).date()
    last_day = (end - timedelta(seconds=1)).astimezone(ZoneInfo(timezone)).date()

    frames: list[pd.DataFrame] = []
    current = first_day
    while current <= last_day:
        frame = fetch_hourly_day(
            station["jma_prec_no"],
            station["jma_block_no"],
            current,
            timezone=timezone,
        )
        frame.insert(0, "station_name", station["name"])
        frame.insert(1, "station_name_ja", station["name_ja"])
        frame.insert(2, "station_elevation_m", float(station["elevation_m"]))
        frame.insert(3, "station_lat", float(station["lat"]))
        frame.insert(4, "station_lon", float(station["lon"]))
        frames.append(frame)
        current += timedelta(days=1)

    result = pd.concat(frames, ignore_index=True)
    end_times = pd.to_datetime(result["time_end_jst"], utc=True)
    start_utc = pd.Timestamp(start).tz_convert("UTC")
    end_utc = pd.Timestamp(end).tz_convert("UTC")
    mask = (end_times > start_utc) & (end_times <= end_utc)
    return result.loc[mask].reset_index(drop=True)


def wind_components(speed_m_s: np.ndarray, direction_from_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Meteorological direction-from to eastward/northward velocity components."""
    radians = np.deg2rad(direction_from_deg)
    u = -speed_m_s * np.sin(radians)
    v = -speed_m_s * np.cos(radians)
    return u, v
