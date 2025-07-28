import math

from point.view import PointWithScale


class CoordinatesService:
    __EARTH_RADIUS = 6_378_137
    __INITIAL_RESOLUTION = 156_543.03392804062

    __SCALE_RULES: dict[int, int | None] = {
         3: 25,
         4: 37,
         5: 48,
         6: 45,
         7: 35,
         8: 40,
         9: 48,
         10: 55,
         11: 55,
         12: 70,
         13: 70,
         14: 55,
         15: 45,
         16: 35,
         17: 30,
         18: 35,
         19: None,
         20: None,
         21: None,
         22: None
    }

    @classmethod
    def process_scale(cls, scale: int) -> int | None:
        return cls.__SCALE_RULES.get(scale, 0)

    @classmethod
    def latlon_bounds_mercator(cls, location: PointWithScale):
        resolution = cls.__INITIAL_RESOLUTION / (2 ** location.scale)

        width_m = location.view_port_size.width * resolution
        height_m = location.view_port_size.height * resolution

        x = cls.__lon_to_m(float(location.longitude))
        y = cls.__lat_to_m(float(location.latitude))

        half_width = math.ceil(width_m / 2)
        half_height = math.ceil(height_m / 2)

        x_min = x - half_width
        x_max = x + half_width
        y_min = y - half_height
        y_max = y + half_height

        lat_min = cls.__m_to_lat(y_min)
        lat_max = cls.__m_to_lat(y_max)
        lon_min = cls.__m_to_lon(x_min)
        lon_max = cls.__m_to_lon(x_max)

        return lon_min, lat_min, lon_max, lat_max

    @classmethod
    def __lat_to_m(cls, lat_deg: float) -> float:
        return cls.__EARTH_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(float(lat_deg)) / 2))

    @classmethod
    def __lon_to_m(cls, lon_deg: float) -> float:
        return cls.__EARTH_RADIUS * lon_deg * math.pi / 180

    @classmethod
    def __m_to_lat(cls, y: float) -> float:
        return math.degrees(2 * math.atan(math.exp(y / cls.__EARTH_RADIUS)) - math.pi / 2)

    @classmethod
    def __m_to_lon(cls, x: float) -> float:
        return math.degrees(x / cls.__EARTH_RADIUS)
