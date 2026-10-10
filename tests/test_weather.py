from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from pipeline.weather.build_historical_forcing import (
    snow_fraction_from_temperature,
    solar_position,
)
from pipeline.weather.jma_history import (
    numeric_value,
    wind_components,
    wind_direction_degrees,
)


def test_jma_numeric_value_handles_quality_markers():
    assert numeric_value("0.5 ]") == 0.5
    assert numeric_value("-12.3 )") == -12.3
    assert np.isnan(numeric_value("///"))
    assert np.isnan(numeric_value("--"))


def test_japanese_wind_directions():
    assert wind_direction_degrees("北") == 0.0
    assert wind_direction_degrees("東") == 90.0
    assert wind_direction_degrees("南") == 180.0
    assert wind_direction_degrees("西") == 270.0
    assert wind_direction_degrees("北北西") == 337.5
    assert np.isnan(wind_direction_degrees("静穏"))


def test_meteorological_wind_components():
    speed = np.asarray([10.0, 10.0, 10.0, 10.0])
    direction = np.asarray([0.0, 90.0, 180.0, 270.0])
    u, v = wind_components(speed, direction)
    assert np.allclose(u, [0.0, -10.0, 0.0, 10.0], atol=1e-6)
    assert np.allclose(v, [-10.0, 0.0, 10.0, 0.0], atol=1e-6)


def test_snow_fraction_temperature_ramp():
    values = snow_fraction_from_temperature(
        np.asarray([-5.0, -1.0, 0.5, 2.0, 5.0], dtype=np.float32)
    )
    assert np.allclose(values, [1.0, 1.0, 0.5, 0.0, 0.0])


def test_winter_midday_sun_is_south_and_above_horizon():
    jst = ZoneInfo("Asia/Tokyo")
    altitude, azimuth = solar_position(
        datetime(2026, 1, 1, 12, 0, tzinfo=jst),
        latitude_deg=43.4,
        longitude_deg=142.64,
    )
    assert np.degrees(altitude) > 15
    assert 150 < np.degrees(azimuth) < 210


def test_winter_midnight_sun_is_below_horizon():
    jst = ZoneInfo("Asia/Tokyo")
    altitude, _ = solar_position(
        datetime(2026, 1, 1, 0, 0, tzinfo=jst),
        latitude_deg=43.4,
        longitude_deg=142.64,
    )
    assert altitude < 0
