#!/usr/bin/env python3
"""
Система сеток
Отвечает за рисование и управление сеткой на главной панели
Сетка всегда отображается поверх всех элементов
"""


class GridSystem:
    """Управление сеткой на холсте"""

    # Минимальный и максимальный размер сетки
    MIN_GRID_SIZE = 5
    MAX_GRID_SIZE = 200
    GRID_SIZE_STEP = 5

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        self.grid_enabled = False
        self.grid_size = config.GRID_SIZE  # Текущий размер сетки
        
        # Ссылка на главную панель
        self.main_panel = None
        
        # Система масштабирования
        self.zoom_system = None

    def set_main_panel(self, panel):
        """Устанавливает главную панель для отрисовки сетки"""
        self.main_panel = panel

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system

    def toggle_grid(self):
        """Включает/выключает сетку"""
        self.grid_enabled = not self.grid_enabled
        if self.grid_enabled:
            self.draw_grid()
        else:
            self.clear_grids()
        return self.grid_enabled

    def increase_size(self):
        """Увеличивает размер сетки"""
        new_size = self.grid_size + self.GRID_SIZE_STEP
        if new_size <= self.MAX_GRID_SIZE:
            self.grid_size = new_size
            print(f"[GridSystem] Размер увеличен до {self.grid_size}px")
            if self.grid_enabled:
                self.draw_grid()
        return self.grid_size

    def decrease_size(self):
        """Уменьшает размер сетки"""
        new_size = self.grid_size - self.GRID_SIZE_STEP
        if new_size >= self.MIN_GRID_SIZE:
            self.grid_size = new_size
            if self.grid_enabled:
                self.draw_grid()
        return self.grid_size

    def get_size(self):
        """Возвращает текущий размер сетки"""
        return self.grid_size

    def is_enabled(self):
        """Проверяет, включена ли сетка"""
        return self.grid_enabled

    def is_any_grid_enabled(self):
        """Проверяет, включена ли сетка (для совместимости)"""
        return self.grid_enabled

    def draw_grid(self):
        """Рисует сетку на главной панели (поверх всех элементов)"""
        self.clear_grids()
        
        if not self.grid_enabled or not self.main_panel:
            return
        
        print(f"[GridSystem] Рисуем сетку размером {self.grid_size}px")
        
        # Получаем экранные координаты главной панели
        if self.zoom_system:
            x1, y1 = self.zoom_system.real_to_screen(self.main_panel.x, self.main_panel.y)
            width = self.zoom_system.scale_value(self.main_panel.width)
            height = self.zoom_system.scale_value(self.main_panel.height)
            grid_size = self.zoom_system.scale_value(self.grid_size)
        else:
            x1, y1 = self.main_panel.x, self.main_panel.y
            width = self.main_panel.width
            height = self.main_panel.height
            grid_size = self.grid_size
        
        if width <= 0 or height <= 0 or grid_size < 2:
            return
        
        x2 = x1 + width
        y2 = y1 + height
        
        # Вычисляем количество полных квадратов
        num_squares_x = int(width) // int(grid_size)
        num_squares_y = int(height) // int(grid_size)
        
        if num_squares_x <= 0 or num_squares_y <= 0:
            return
        
        # Вычисляем размер области с полными квадратами
        grid_width = num_squares_x * grid_size
        grid_height = num_squares_y * grid_size
        
        # Смещение для центрирования
        offset_x = x1 + (width - grid_width) / 2
        offset_y = y1 + (height - grid_height) / 2
        
        color = self.config.GRID_COLOR
        
        # Вертикальные линии
        x = offset_x
        while x <= offset_x + grid_width + 0.5:
            item = self.canvas.create_line(
                x, offset_y, x, offset_y + grid_height,
                fill=color, tags="grid"
            )
            # Поднимаем сетку наверх
            self.canvas.tag_raise(item)
            x += grid_size
        
        # Горизонтальные линии
        y = offset_y
        while y <= offset_y + grid_height + 0.5:
            item = self.canvas.create_line(
                offset_x, y, offset_x + grid_width, y,
                fill=color, tags="grid"
            )
            # Поднимаем сетку наверх
            self.canvas.tag_raise(item)
            y += grid_size

    def clear_grids(self):
        """Удаляет сетку"""
        self.canvas.delete("grid")

    def draw_grids_on_element(self, element):
        """Рисует сетку (для совместимости)"""
        # Сетка рисуется только на главной панели
        self.draw_grid()

    # Устаревшие методы (для совместимости)
    def toggle_grid1(self):
        """Для совместимости"""
        return self.toggle_grid()

    def toggle_grid2(self):
        """Убрано - теперь используем кнопки размера"""
        pass
