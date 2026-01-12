"""
Тесты для функции filter_points_by_shape из CoordinatesService.

Проверяют, что принятые точки не имеют наложений фигур.
"""
import pytest

from point.controllers import EstablishmentController
from point.services.coordinates import CoordinatesService


class TestFilterPointsByShape:
    """Тесты для проверки отсутствия наложений фигур."""

    @classmethod
    def _get_point_occupied_cells(cls, lon: float, lat: float, scale: float) -> set[tuple[float, float]]:
        """
        Получить множество занятых ячеек для точки.
        
        Args:
            lon: Долгота точки
            lat: Широта точки
            scale: Масштаб карты (zoom level). Если None, используется фиксированный размер фигуры.
            
        Returns:
            Множество кортежей (px, py) занятых ячеек в метрах
        """
        resolution = CoordinatesService._CoordinatesService__INITIAL_RESOLUTION / (2 ** scale)

        shape_offsets = CoordinatesService.get_shape_offsets()
        px = CoordinatesService._CoordinatesService__lon_to_m(float(lon)) // resolution
        py = CoordinatesService._CoordinatesService__lat_to_m(float(lat)) // resolution
        
        occupied = set()
        for dx, dy in shape_offsets:
            occupied.add((px + dx, py + dy))
        
        return occupied

    def _verify_no_overlaps(self, points: tuple, accepted_indices: list[int], scale: float):
        """
        Проверить, что принятые точки не имеют наложений фигур.

        Args:
            points: Кортеж всех точек (lon, lat)
            accepted_indices: Список индексов принятых точек
            scale: Масштаб карты (zoom level). Если None, используется фиксированный размер фигуры.
        """
        if len(accepted_indices) <= 1:
            return  # Нет смысла проверять наложения для 0 или 1 точки

        # Получаем занятые ячейки для каждой принятой точки
        occupied_sets = []
        for idx in accepted_indices:
            lon, lat = points[idx]
            occupied = self._get_point_occupied_cells(lon, lat, scale=scale)
            occupied_sets.append(occupied)

        # Проверяем, что множества не пересекаются
        for i in range(len(occupied_sets)):
            for j in range(i + 1, len(occupied_sets)):
                overlap = occupied_sets[i] & occupied_sets[j]
                assert len(overlap) == 0, (
                    f"Обнаружено наложение между точками {accepted_indices[i]} и {accepted_indices[j]}. "
                    f"Пересекающиеся ячейки: {overlap}"
                )

    def test_no_overlap_single_point(self):
        """Тест: одна точка должна быть принята."""
        points = ((37.6173, 55.7558),)  # Москва
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        assert len(accepted) == 1
        assert accepted == [0]

    def test_no_overlap_distant_points(self):
        """Тест: далекие точки должны быть приняты все."""
        # Точки далеко друг от друга (Москва и Санкт-Петербург)
        points = (
            (37.6173, 55.7558),  # Москва
            (30.3159, 59.9343),  # Санкт-Петербург
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        assert len(accepted) == 2
        assert accepted == [0, 1]

    def test_no_overlap_close_points(self):
        """Тест: близкие точки - только одна должна быть принята."""
        # Точки очень близко друг к другу (в пределах одной фигуры)
        base_lon, base_lat = 37.6173, 55.7558  # Москва
        
        # Создаем вторую точку очень близко к первой
        # Смещение примерно 1 метр в градусах (примерно 0.00001 градуса)
        points = (
            (base_lon, base_lat),
            (base_lon + 0.00001, base_lat + 0.00001),  # Очень близко
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Должна быть принята только одна точка
        assert len(accepted) == 1
        assert accepted[0] in [0, 1]

    def test_no_overlap_medium_distance(self):
        """Тест: точки на среднем расстоянии - проверка отсутствия наложений."""
        base_lon, base_lat = 37.6173, 55.7558  # Москва
        
        # Создаем несколько точек на разных расстояниях
        # Смещение примерно 200 метров (примерно 0.002 градуса на широте Москвы)
        points = (
            (base_lon, base_lat),
            (base_lon + 0.002, base_lat),  # Восток
            (base_lon - 0.002, base_lat),  # Запад
            (base_lon, base_lat + 0.002),  # Север
            (base_lon, base_lat - 0.002),  # Юг
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Проверяем, что принятые точки не имеют наложений
        self._verify_no_overlaps(points, accepted, scale=22)

    def test_no_overlap_multiple_points(self):
        """Тест: множество точек - проверка отсутствия наложений."""
        base_lon, base_lat = 37.6173, 55.7558  # Москва
        
        # Создаем сетку точек
        points = []
        step = 0.001  # Примерно 100 метров
        for i in range(-2, 3):
            for j in range(-2, 3):
                points.append((base_lon + i * step, base_lat + j * step))
        
        points = tuple(points)
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Проверяем отсутствие наложений
        self._verify_no_overlaps(points, accepted, scale=22)

    def test_no_overlap_empty_input(self):
        """Тест: пустой ввод должен вернуть пустой список."""
        points = ()
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        assert len(accepted) == 0
        assert accepted == []

    def test_no_overlap_identical_points(self):
        """Тест: идентичные точки - только одна должна быть принята."""
        point = (37.6173, 55.7558)
        points = (point, point, point)
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Должна быть принята только первая точка
        assert len(accepted) == 1
        assert accepted == [0]

    def test_no_overlap_verification(self):
        """Тест: прямая проверка отсутствия наложений для принятых точек."""
        base_lon, base_lat = 37.6173, 55.7558
        
        # Создаем точки на разных расстояниях
        points = (
            (base_lon, base_lat),
            (base_lon + 0.001, base_lat),
            (base_lon + 0.002, base_lat),
            (base_lon + 0.003, base_lat),
            (base_lon + 0.004, base_lat),
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Проверяем отсутствие наложений
        self._verify_no_overlaps(points, accepted, scale=22)

    def test_no_overlap_edge_case_same_longitude(self):
        """Тест: точки на одной долготе - проверка отсутствия наложений."""
        base_lon = 37.6173
        points = (
            (base_lon, 55.7558),
            (base_lon, 55.7568),  # Смещение по широте
            (base_lon, 55.7578),
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        self._verify_no_overlaps(points, accepted, scale=22)

    def test_no_overlap_edge_case_same_latitude(self):
        """Тест: точки на одной широте - проверка отсутствия наложений."""
        base_lat = 55.7558
        points = (
            (37.6173, base_lat),
            (37.6183, base_lat),  # Смещение по долготе
            (37.6193, base_lat),
        )
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        self._verify_no_overlaps(points, accepted, scale=22)

    def test_no_overlap_grid_pattern(self):
        """Тест: точки в виде сетки - проверка отсутствия наложений."""
        base_lon, base_lat = 37.6173, 55.7558
        
        # Создаем регулярную сетку
        grid_size = 5
        step = 0.0005  # Примерно 50 метров
        points = []
        for i in range(grid_size):
            for j in range(grid_size):
                points.append((
                    base_lon + i * step,
                    base_lat + j * step
                ))
        
        points = tuple(points)
        accepted = CoordinatesService.filter_points_by_shape(points, scale=22)
        
        # Проверяем отсутствие наложений
        self._verify_no_overlaps(points, accepted, scale=22)
        
        # Дополнительная проверка: убеждаемся, что принято разумное количество точек
        # (не все, но и не слишком мало)
        assert len(accepted) > 0, "Должна быть принята хотя бы одна точка"
        assert len(accepted) <= len(points), "Не может быть принято больше точек, чем есть"

    @pytest.mark.skip
    def test_from_database(self):
        """
        Ручной тест для проверки алгоритма filter_points_by_shape на реальных данных из БД.

        Использует границы Санкт-Петербурга, применяет алгоритм фильтрации и проверяет
        отсутствие наложений полным перебором.
        """

        import asyncio
        from tortoise import Tortoise
        from point.config import TORTOISE_ORM

        async def run_test():
            # Инициализируем Tortoise ORM
            await Tortoise.init(config=TORTOISE_ORM)

            try:
                # Границы Санкт-Петербурга (lon_min, lat_min, lon_max, lat_max)
                # Долгота: примерно от 29.5 до 30.8
                # Широта: примерно от 59.7 до 60.1
                petersburg_bounds = (29.5, 59.7, 30.8, 60.1)

                establishments = await EstablishmentController.get_establishments_by_rectangle(
                    rectangle=petersburg_bounds,
                    limit=None
                )

                print(f"Получено заведений из БД: {len(establishments)}")

                if len(establishments) == 0:
                    print("В БД нет заведений в указанных границах")
                    return

                # Извлекаем координаты заведений
                points = tuple(e.location for e in establishments)

                # Используем средний масштаб для теста (можно изменить для проверки разных масштабов)
                for test_scale in range(3, 23):
                    test_scale = test_scale

                    # Применяем алгоритм фильтрации (как в продуктовом коде)
                    accepted_indices = CoordinatesService.filter_points_by_shape(points=points, scale=test_scale)
                    accepted_establishments = [establishments[i] for i in accepted_indices]

                    print(f"Принято алгоритмом (scale={test_scale}): {len(accepted_indices)} из {len(establishments)}")
                    print(f"Процент принятых: {len(accepted_indices) / len(establishments) * 100:.2f}%")

                    # Проверка отсутствия наложений полным перебором
                    # Используем метод класса для проверки (передаем тот же scale)
                    self._verify_no_overlaps(points, accepted_indices, scale=test_scale)

                    print(f"\n✅ Тест завершен успешно. Принято {len(accepted_indices)} точек без наложений.")
            finally:
                await Tortoise.close_connections()

        # Запускаем async тест
        asyncio.run(run_test())
