#!/usr/bin/env python3
"""
Элемент: Кнопка (Button)
Интерактивный элемент с привязкой к функции
При ПКМ открывается окно настройки для задания номера функции
"""
from ..element_base import ElementBase


class ButtonElement(ElementBase):
    """Кнопка - интерактивный элемент"""

    ELEMENT_TYPE = "button"
    ELEMENT_SYMBOL = "▣"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Настройки по умолчанию для кнопки
        self.properties.update({
            'fill_color': '#3a3a3a',
            'stroke_color': '#5a5a5a',
            'stroke_width': 1,
            'display_mode': 'both',
            'corner_radius': 6,
            
            # Специфичные для кнопки
            'button_text': '',           # Текст на кнопке
            'button_function_id': 0,     # ID функции для вызова
            'hover_color': '#4a4a4a',    # Цвет при наведении
            'active_color': '#2a2a2a',   # Цвет при нажатии
        })
        
        # Текст на кнопке
        self._text_item = None

    def draw(self):
        """Рисует кнопку"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Получаем свойства
        stroke_color = self.properties['stroke_color']
        stroke_width = self._scale(self.properties['stroke_width'])
        fill_color = self.properties['fill_color'] or '#3a3a3a'
        display_mode = self.properties['display_mode']
        
        # Радиусы углов
        radii = self._get_corner_radii()
        shape = self.properties['shape']
        if shape == 'pill':
            r = min(x2 - x1, y2 - y1) / 2
            radii = (r, r, r, r)
        radii = tuple(self._scale(r) for r in radii)
        
        chamfer = self._scale(self.properties['chamfer_size'])
        dash = self._get_dash_pattern()
        
        draw_fill = display_mode in ('fill', 'both')
        draw_stroke = display_mode in ('stroke', 'both') and stroke_color
        stroke_width = max(1, stroke_width) if draw_stroke else 0

        # Тень
        if self.properties['shadow_enabled']:
            self._draw_shadow(x1, y1, x2, y2, shape, radii, chamfer)

        # Свечение
        if self.properties['glow_enabled']:
            self._draw_glow(x1, y1, x2, y2, shape, radii, chamfer)

        # Основная форма кнопки
        self._draw_shape(
            x1, y1, x2, y2, shape, radii, chamfer,
            fill=fill_color if draw_fill else '',
            outline=stroke_color if draw_stroke else '',
            width=stroke_width,
            dash=dash
        )

        # Текст кнопки
        self._draw_button_text(x1, y1, x2, y2)
        
        # Индикатор функции (маленький номер в углу)
        self._draw_function_indicator(x1, y1, x2, y2)

    def _draw_button_text(self, x1, y1, x2, y2):
        """Рисует текст на кнопке"""
        text = self.properties.get('button_text', '')
        if not text:
            return
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Масштабируем размер шрифта
        font_size = max(10, int(self._scale(12)))
        
        item = self.canvas.create_text(
            center_x, center_y,
            text=text,
            fill="#ffffff",
            font=("Arial", font_size),
            anchor="center",
            tags=("element", self.id, "button_text")
        )
        self.canvas_items.append(item)

    def _draw_function_indicator(self, x1, y1, x2, y2):
        """Рисует индикатор номера функции"""
        func_id = self.properties.get('button_function_id', 0)
        if func_id <= 0:
            return
        
        # Позиция в правом верхнем углу
        indicator_x = x2 - 8
        indicator_y = y1 + 8
        
        # Фон индикатора
        bg = self.canvas.create_oval(
            indicator_x - 8, indicator_y - 8,
            indicator_x + 8, indicator_y + 8,
            fill="#ff6600",
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

    def get_function_id(self):
        """Возвращает ID привязанной функции"""
        return self.properties.get('button_function_id', 0)

    def set_function_id(self, func_id):
        """Устанавливает ID функции"""
        self.properties['button_function_id'] = func_id
        self.update()

    def set_button_text(self, text):
        """Устанавливает текст кнопки"""
        self.properties['button_text'] = text
        self.update()

