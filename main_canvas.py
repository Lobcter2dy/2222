#!/usr/bin/env python3
"""
Главная панель (Main Canvas)
Чёрная основа для всех элементов
Всегда на заднем плане, не является элементом
"""


class MainCanvas:
    """Главная чёрная панель"""

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Позиция и размеры
        self.x = 0
        self.y = 0
        self.width = config.WORK_ZONE_DEFAULT_WIDTH
        self.height = config.WORK_ZONE_DEFAULT_HEIGHT
        
        # Свойства (совместимы с tab_color)
        self.properties = {
            'fill_color': '#000000',
            'stroke_color': '#333333',
            'stroke_width': 1,
        }
        
        # Canvas объекты
        self._canvas_items = []
        
        # Система масштабирования
        self.zoom_system = None
        self.is_visible = True

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system

    def get_screen_bounds(self):
        """Возвращает экранные координаты"""
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(self.x, self.y)
            sw = self.zoom_system.scale_value(self.width)
            sh = self.zoom_system.scale_value(self.height)
            return (sx, sy, sx + sw, sy + sh)
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def get_bounds(self):
        """Возвращает реальные координаты"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def draw(self):
        """Рисует панель (на заднем плане)"""
        self.clear()
        
        if not self.is_visible:
            return
        
        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Проверяем что координаты корректные
        if x2 <= x1 or y2 <= y1:
            print(f"[MainCanvas] Некорректные координаты: ({x1},{y1}) - ({x2},{y2})")
            return
        
        stroke_width = self.properties['stroke_width']
        if self.zoom_system:
            stroke_width = max(1, self.zoom_system.scale_value(stroke_width))
        
        # УБИРАЕМ отладку - она засоряет лог
        item = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.properties['fill_color'],
            outline=self.properties['stroke_color'],
            width=stroke_width,
            tags=("main_canvas",)
        )
        self._canvas_items.append(item)
        self.canvas.tag_lower(item)

    def clear(self):
        """Удаляет графику"""
        for item in self._canvas_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Canvas item already deleted
        self._canvas_items = []

    def update(self):
        """Перерисовывает"""
        self.draw()

    def resize(self, width, height):
        """Изменяет размер"""
        self.width = max(100, width)
        self.height = max(100, height)
        self.update()

    def move_to(self, x, y):
        """Перемещает"""
        self.x = x
        self.y = y
        self.update()

    def center_on_canvas(self):
        """Центрирует на холсте"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        print(f"[MainCanvas] Центрирование: холст {canvas_width}×{canvas_height}, панель {self.width}×{self.height}")
        
        if canvas_width > 1 and canvas_height > 1:
            self.x = (canvas_width - self.width) // 2
            self.y = (canvas_height - self.height) // 2
            print(f"[MainCanvas] Новая позиция: ({self.x}, {self.y})")
            self.update()
        else:
            # Если размеры холста ещё не известны - устанавливаем видимую позицию
            self.x = 50
            self.y = 50
            print(f"[MainCanvas] Временная позиция: ({self.x}, {self.y})")
            self.update()

    def contains_point(self, screen_x, screen_y):
        """Проверяет попадание точки"""
        x1, y1, x2, y2 = self.get_screen_bounds()
        return x1 <= screen_x <= x2 and y1 <= screen_y <= y2

    def set_properties(self, props):
        """Устанавливает свойства"""
        for key in ['fill_color', 'stroke_color', 'stroke_width']:
            if key in props:
                self.properties[key] = props[key]
        self.update()

    def get_properties(self):
        """Возвращает свойства"""
        return self.properties.copy()

    def to_lower(self):
        """Опускает на задний план"""
        for item in self._canvas_items:
            self.canvas.tag_lower(item)
