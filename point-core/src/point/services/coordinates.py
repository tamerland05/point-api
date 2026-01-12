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

    __SHAPE_OFFSETS = None

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
    def filter_points_by_shape(cls, points: tuple, scale: float) -> list[int]:
        shape_offsets = cls.get_shape_offsets()
        
        resolution = cls.__INITIAL_RESOLUTION / (2 ** scale)

        occupied = set()
        accepted_indices = []

        for i in range(len(points)):
            lon, lat = points[i]
            px = cls.__lon_to_m(float(lon)) // resolution
            py = cls.__lat_to_m(float(lat)) // resolution

            blocked = False
            for dx, dy in shape_offsets:
                if (px + dx, py + dy) in occupied:
                    blocked = True
                    break
            if blocked:
                continue

            for dx, dy in shape_offsets:
                occupied.add((px + dx, py + dy))

            accepted_indices.append(i)

        return accepted_indices

    @classmethod
    def get_shape_offsets(cls):
        if cls.__SHAPE_OFFSETS is None:
            cls.__SHAPE_OFFSETS = cls.__shape_offsets()
        return cls.__SHAPE_OFFSETS

    @classmethod
    def __shape_offsets(
            cls,
            circle_visible_radius: int = 20,
            safety: int = 5,
            rect_width: int = 100,
            rect_height: int = 16,
    ) -> tuple[tuple[int, int]]:
        R_vis = circle_visible_radius
        R = circle_visible_radius + safety

        half_w = rect_width // 2
        y_top = -R_vis
        y_bottom = y_top - rect_height

        shape_points = set()

        for x in range(0, R + 1):
            y = int(round(math.sqrt(R * R - x * x)))

            for perimeter_point in [(x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)]:
                shape_points.add(perimeter_point)

        for (cx, cy) in list(shape_points):
            if cy <= y_top:
                shape_points.remove((cx, cy))

        sorted_by_y = sorted(shape_points, key=lambda p: p[1])
        left_x = sorted_by_y[0][0]
        right_x = sorted_by_y[1][0]

        for y in range(y_bottom, y_top + 1):
            left = (-half_w, y)
            right = (half_w, y)
            if left not in shape_points:
                shape_points.add(left)
            if right not in shape_points:
                shape_points.add(right)

        for x in range(-half_w, half_w + 1):
            shape_points.add((x, y_bottom))

            if left_x <= x <= right_x:
                continue
            shape_points.add((x, y_top))

        return tuple(shape_points)

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


CoordinatesService.get_shape_offsets()
