from decimal import Decimal

from point.view import PointRequestIn


def point_distance(point1: PointRequestIn, point2: PointRequestIn) -> Decimal:
    return (
            (point1.latitude - point2.latitude) ** 2 +
            (point1.longitude - point2.longitude) ** 2
    ).sqrt()
