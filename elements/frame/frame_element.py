#!/usr/bin/env python3
"""
Элемент: Рамка (Frame)
Геометрический элемент с обводкой
Поддерживает различные формы, стили линий, двойную рамку
"""
from ..element_base import ElementBase


class FrameElement(ElementBase):
    """Рамка - геометрический примитив с обводкой"""

    ELEMENT_TYPE = "frame"
    ELEMENT_SYMBOL = "□"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Настройки по умолчанию для рамки
        self.properties.update({
            'fill_color': '',           # Прозрачная заливка
            'stroke_color': '#ffffff',  # Белая обводка
            'stroke_width': 2,
            'display_mode': 'stroke',   # Только обводка
            
            # Специфичные для рамки
            'frame_function_id': 0,     # ID привязанной функции
            'spawn_points': [],         # Точки появления: [{'x': 0, 'y': 0, 'id': 1}, ...]
        })

    def draw(self):
        """Рисует рамку"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Получаем свойства
        stroke_color = self.properties['stroke_color']
        stroke_width = self._scale(self.properties['stroke_width'])
        fill_color = self.properties['fill_color'] or ''
        display_mode = self.properties['display_mode']
        shape = self.properties['shape']
        
        # Радиусы углов
        radii = self._get_corner_radii()
        if shape == 'pill':
            r = min(x2 - x1, y2 - y1) / 2
            radii = (r, r, r, r)
        radii = tuple(self._scale(r) for r in radii)
        
        # Размер скоса
        chamfer = self._scale(self.properties['chamfer_size'])
        
        # Паттерн пунктира
        dash = self._get_dash_pattern()
        
        # Определяем что рисовать
        draw_fill = display_mode in ('fill', 'both') and fill_color
        draw_stroke = display_mode in ('stroke', 'both') and stroke_color
        
        stroke_width = max(1, stroke_width) if draw_stroke else 0

        # 1. Тень (на заднем плане)
        if self.properties['shadow_enabled']:
            self._draw_shadow(x1, y1, x2, y2, shape, radii, chamfer)

        # 2. Свечение
        if self.properties['glow_enabled']:
            self._draw_glow(x1, y1, x2, y2, shape, radii, chamfer)

        # 3. Двойная рамка (внешняя)
        if self.properties['double_border'] and draw_stroke:
            gap = self._scale(self.properties['double_border_gap'])
            outer_color = self.properties['double_border_color'] or stroke_color
            outer_radii = tuple(r + gap for r in radii)
            
            self._draw_shape(
                x1 - gap, y1 - gap, x2 + gap, y2 + gap,
                shape, outer_radii, chamfer + gap,
                fill='', outline=outer_color, width=stroke_width, dash=dash
            )

        # 4. Основная форма
        self._draw_shape(
            x1, y1, x2, y2, shape, radii, chamfer,
            fill=fill_color if draw_fill else '',
            outline=stroke_color if draw_stroke else '',
            width=stroke_width,
            dash=dash
        )

        # 5. Внутренняя тень
        if self.properties['inset_shadow'] and draw_fill:
            self._draw_inset_shadow(x1, y1, x2, y2, shape, radii, chamfer)
        
        # 6. Точки появления
        self._draw_spawn_points(x1, y1)
        
        # 7. Индикатор функции
        if self.properties.get('frame_function_id', 0) > 0:
            self._draw_function_indicator(x1, y1)

    def _draw_shadow(self, x1, y1, x2, y2, shape, radii, chamfer):
        """Рисует тень"""
        sx = self._scale(self.properties['shadow_x'])
        sy = self._scale(self.properties['shadow_y'])
        color = self.properties['shadow_color']
        
        self._draw_shape(
            x1 + sx, y1 + sy, x2 + sx, y2 + sy,
            shape, radii, chamfer,
            fill=color, outline='',
            tags=("element", self.id, "shadow")
        )

    def _draw_glow(self, x1, y1, x2, y2, shape, radii, chamfer):
        """Рисует свечение"""
        radius = self._scale(self.properties['glow_radius'])
        color = self.properties['glow_color']
        glow_radii = tuple(r + radius for r in radii)
        
        self._draw_shape(
            x1 - radius, y1 - radius, x2 + radius, y2 + radius,
            shape, glow_radii, chamfer + radius,
            fill='', outline=color, width=radius,
            tags=("element", self.id, "glow")
        )

    def _draw_inset_shadow(self, x1, y1, x2, y2, shape, radii, chamfer):
        """Рисует внутреннюю тень"""
        size = self._scale(self.properties['inset_shadow_size'])
        color = self.properties['inset_shadow_color']
        
        # Рисуем несколько слоёв
        for i in range(max(1, int(size))):
            offset = i
            inner_radii = tuple(max(0, r - offset) for r in radii)
            
            self._draw_shape(
                x1 + offset, y1 + offset, x2 - offset, y2 - offset,
                shape, inner_radii, max(0, chamfer - offset),
                fill='', outline=color, width=1,
                tags=("element", self.id, "inset")
            )

    def _draw_spawn_points(self, base_x, base_y):
        """Рисует точки появления"""
        spawn_points = self.properties.get('spawn_points', [])
        if not spawn_points:
            return
        
        for point in spawn_points:
            px = point.get('x', 0)
            py = point.get('y', 0)
            pid = point.get('id', 0)
            
            # Преобразуем координаты относительно элемента
            screen_x = base_x + self._scale(px)
            screen_y = base_y + self._scale(py)
            
            point_size = 6
            
            # Рисуем точку (крестик + круг)
            # Круг
            circle = self.canvas.create_oval(
                screen_x - point_size, screen_y - point_size,
                screen_x + point_size, screen_y + point_size,
                fill="#00ff00",
                outline="#ffffff",
                width=1,
                tags=("element", self.id, "spawn_point")
            )
            self.canvas_items.append(circle)
            
            # Крестик
            line1 = self.canvas.create_line(
                screen_x - point_size + 2, screen_y,
                screen_x + point_size - 2, screen_y,
                fill="#000000",
                width=2,
                tags=("element", self.id, "spawn_point")
            )
            self.canvas_items.append(line1)
            
            line2 = self.canvas.create_line(
                screen_x, screen_y - point_size + 2,
                screen_x, screen_y + point_size - 2,
                fill="#000000",
                width=2,
                tags=("element", self.id, "spawn_point")
            )
            self.canvas_items.append(line2)
            
            # Номер точки
            if pid > 0:
                label = self.canvas.create_text(
                    screen_x + point_size + 8, screen_y,
                    text=str(pid),
                    fill="#00ff00",
                    font=("Arial", 9, "bold"),
                    anchor="w",
                    tags=("element", self.id, "spawn_point")
                )
                self.canvas_items.append(label)

    def _draw_function_indicator(self, x1, y1):
        """Рисует индикатор номера функции"""
        func_id = self.properties.get('frame_function_id', 0)
        if func_id <= 0:
            return
        
        # Позиция в левом верхнем углу
        indicator_x = x1 + 12
        indicator_y = y1 + 12
        
        # Фон индикатора
        bg = self.canvas.create_oval(
            indicator_x - 10, indicator_y - 10,
            indicator_x + 10, indicator_y + 10,
            fill="#0066cc",
            outline="#ffffff",
            width=1,
            tags=("element", self.id, "func_indicator")
        )
        self.canvas_items.append(bg)
        
        # Номер функции
        text = self.canvas.create_text(
            indicator_x, indicator_y,
            text=str(func_id),
            fill="#ffffff",
            font=("Arial", 9, "bold"),
            anchor="center",
            tags=("element", self.id, "func_indicator")
        )
        self.canvas_items.append(text)

    # === Методы для работы с точками появления ===
    
    def get_function_id(self):
        """Возвращает ID привязанной функции"""
        return self.properties.get('frame_function_id', 0)

    def set_function_id(self, func_id):
        """Устанавливает ID функции"""
        self.properties['frame_function_id'] = func_id
        self.update()

    def get_spawn_points(self):
        """Возвращает список точек появления"""
        return self.properties.get('spawn_points', [])

    def add_spawn_point(self, x, y, point_id=None):
        """Добавляет точку появления"""
        points = self.properties.get('spawn_points', [])
        if point_id is None:
            point_id = len(points) + 1
        points.append({'x': x, 'y': y, 'id': point_id})
        self.properties['spawn_points'] = points
        self.update()

    def remove_spawn_point(self, index):
        """Удаляет точку появления по индексу"""
        points = self.properties.get('spawn_points', [])
        if 0 <= index < len(points):
            del points[index]
            self.properties['spawn_points'] = points
            self.update()

    def move_spawn_point(self, index, new_x, new_y):
        """Перемещает точку появления"""
        points = self.properties.get('spawn_points', [])
        if 0 <= index < len(points):
            points[index]['x'] = new_x
            points[index]['y'] = new_y
            self.properties['spawn_points'] = points
            self.update()
