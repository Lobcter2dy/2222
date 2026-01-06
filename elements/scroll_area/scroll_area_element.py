#!/usr/bin/env python3
"""
Элемент: Область прокрутки (Scroll Area)
Контейнер с возможностью прокрутки содержимого
"""
import tkinter as tk
from ..element_base import ElementBase


class ScrollAreaElement(ElementBase):
    """Область прокрутки - контейнер с прокруткой содержимого"""

    ELEMENT_TYPE = "scroll_area"
    ELEMENT_SYMBOL = "⊞"

    # Направления прокрутки
    SCROLL_DIRECTIONS = {
        'both': 'Оба направления',
        'vertical': 'Вертикальная',
        'horizontal': 'Горизонтальная',
        'none': 'Без прокрутки'
    }

    # Стили полос прокрутки
    SCROLLBAR_STYLES = {
        'auto': 'Автоматически',
        'always': 'Всегда видны',
        'never': 'Скрыты',
        'hover': 'При наведении'
    }

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Размеры по умолчанию
        self.width = 300
        self.height = 200
        
        # Содержимое (виртуальные размеры)
        self.content_width = 500
        self.content_height = 400
        
        # Текущая позиция прокрутки (0-1)
        self.scroll_x = 0.0
        self.scroll_y = 0.0
        
        # Состояние взаимодействия
        self._dragging_scrollbar = None  # 'h' или 'v'
        self._drag_start = None
        self._scroll_start = None
        
        # Настройки
        self.properties.update({
            # === Основные настройки ===
            'scroll_direction': 'both',       # both, vertical, horizontal, none
            'scrollbar_style': 'auto',        # auto, always, never, hover
            
            # === Размеры содержимого ===
            'content_width': 500,
            'content_height': 400,
            
            # === Внешний вид области ===
            'background_color': '#1a1a1a',
            'border_color': '#444444',
            'border_width': 1,
            'corner_radius': 4,
            
            # === Полосы прокрутки ===
            'scrollbar_width': 10,
            'scrollbar_track_color': '#2a2a2a',
            'scrollbar_thumb_color': '#666666',
            'scrollbar_thumb_hover': '#888888',
            'scrollbar_thumb_radius': 4,
            
            # === Отступы содержимого ===
            'padding_top': 0,
            'padding_right': 0,
            'padding_bottom': 0,
            'padding_left': 0,
            
            # === Поведение прокрутки ===
            'scroll_speed': 20,               # Скорость прокрутки колесом
            'smooth_scroll': True,            # Плавная прокрутка
            'scroll_momentum': True,          # Инерция прокрутки
            'overscroll': False,              # Перепрокрутка (эффект bounce)
            
            # === Снимок содержимого ===
            'snap_to_grid': False,            # Прилипание к сетке
            'snap_grid_size': 50,
            
            # === Дополнительно ===
            'show_scroll_indicators': True,   # Индикаторы прокрутки
            'clip_content': True,             # Обрезать содержимое
        })

    def draw(self):
        """Рисует область прокрутки"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Размеры
        width = x2 - x1
        height = y2 - y1
        
        # Обновляем размеры содержимого из properties
        self.content_width = self.properties['content_width']
        self.content_height = self.properties['content_height']
        
        # 1. Фон области
        self._draw_background(x1, y1, x2, y2)
        
        # 2. Зона содержимого (визуализация)
        self._draw_content_area(x1, y1, x2, y2)
        
        # 3. Полосы прокрутки
        scrollbar_style = self.properties['scrollbar_style']
        if scrollbar_style != 'never':
            self._draw_scrollbars(x1, y1, x2, y2)
        
        # 4. Индикаторы прокрутки
        if self.properties['show_scroll_indicators']:
            self._draw_scroll_indicators(x1, y1, x2, y2)
        
        # 5. Рамка
        self._draw_border(x1, y1, x2, y2)

    def _draw_background(self, x1, y1, x2, y2):
        """Рисует фон"""
        radius = self._scale(self.properties['corner_radius'])
        color = self.properties['background_color']
        
        if radius > 0:
            self._draw_rounded_rect(x1, y1, x2, y2, radius, fill=color, outline='')
        else:
            bg = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color, outline='',
                tags=("element", self.id, "scroll_bg")
            )
            self.canvas_items.append(bg)

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, fill='', outline='', width=1):
        """Рисует скруглённый прямоугольник"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1,
        ]
        
        item = self.canvas.create_polygon(
            points, smooth=True,
            fill=fill, outline=outline, width=width,
            tags=("element", self.id, "scroll_rounded")
        )
        self.canvas_items.append(item)
        return item

    def _draw_content_area(self, x1, y1, x2, y2):
        """Рисует визуализацию области содержимого"""
        scrollbar_w = self._scale(self.properties['scrollbar_width'])
        direction = self.properties['scroll_direction']
        
        # Учитываем полосы прокрутки
        content_x2 = x2 - (scrollbar_w if direction in ['both', 'vertical'] else 0)
        content_y2 = y2 - (scrollbar_w if direction in ['both', 'horizontal'] else 0)
        
        # Отступы
        pad_t = self._scale(self.properties['padding_top'])
        pad_r = self._scale(self.properties['padding_right'])
        pad_b = self._scale(self.properties['padding_bottom'])
        pad_l = self._scale(self.properties['padding_left'])
        
        cx1 = x1 + pad_l
        cy1 = y1 + pad_t
        cx2 = content_x2 - pad_r
        cy2 = content_y2 - pad_b
        
        # Визуализация содержимого (сетка для демонстрации)
        view_w = cx2 - cx1
        view_h = cy2 - cy1
        
        if view_w > 0 and view_h > 0:
            # Рисуем сетку содержимого
            grid_size = 40
            
            # Смещение на основе прокрутки
            offset_x = self.scroll_x * max(0, self.content_width - view_w)
            offset_y = self.scroll_y * max(0, self.content_height - view_h)
            
            # Вертикальные линии
            for i in range(int(self.content_width / grid_size) + 1):
                lx = cx1 + i * grid_size - offset_x
                if cx1 <= lx <= cx2:
                    line = self.canvas.create_line(
                        lx, max(cy1, cy1), lx, min(cy2, cy2),
                        fill='#333333', width=1, dash=(2, 4),
                        tags=("element", self.id, "scroll_content_grid")
                    )
                    self.canvas_items.append(line)
            
            # Горизонтальные линии
            for i in range(int(self.content_height / grid_size) + 1):
                ly = cy1 + i * grid_size - offset_y
                if cy1 <= ly <= cy2:
                    line = self.canvas.create_line(
                        max(cx1, cx1), ly, min(cx2, cx2), ly,
                        fill='#333333', width=1, dash=(2, 4),
                        tags=("element", self.id, "scroll_content_grid")
                    )
                    self.canvas_items.append(line)
            
            # Метка позиции
            pos_text = f"↕{int(offset_y)} ↔{int(offset_x)}"
            pos_label = self.canvas.create_text(
                cx1 + 8, cy1 + 12,
                text=pos_text,
                font=("Arial", 8),
                fill='#555555',
                anchor="nw",
                tags=("element", self.id, "scroll_pos")
            )
            self.canvas_items.append(pos_label)

    def _draw_scrollbars(self, x1, y1, x2, y2):
        """Рисует полосы прокрутки"""
        direction = self.properties['scroll_direction']
        scrollbar_w = self._scale(self.properties['scrollbar_width'])
        track_color = self.properties['scrollbar_track_color']
        thumb_color = self.properties['scrollbar_thumb_color']
        thumb_radius = self._scale(self.properties['scrollbar_thumb_radius'])
        
        # Вертикальная полоса
        if direction in ['both', 'vertical']:
            # Трек
            v_track_x1 = x2 - scrollbar_w
            v_track_y1 = y1 + 2
            v_track_y2 = y2 - (scrollbar_w + 2 if direction == 'both' else 2)
            
            track = self.canvas.create_rectangle(
                v_track_x1, v_track_y1, x2 - 2, v_track_y2,
                fill=track_color, outline='',
                tags=("element", self.id, "scroll_v_track")
            )
            self.canvas_items.append(track)
            
            # Ползунок
            track_h = v_track_y2 - v_track_y1
            view_h = y2 - y1 - (scrollbar_w if direction == 'both' else 0)
            
            if self.content_height > view_h:
                thumb_h = max(30, track_h * (view_h / self.content_height))
                thumb_y = v_track_y1 + self.scroll_y * (track_h - thumb_h)
                
                thumb = self.canvas.create_rectangle(
                    v_track_x1 + 2, thumb_y,
                    x2 - 4, thumb_y + thumb_h,
                    fill=thumb_color, outline='',
                    tags=("element", self.id, "scroll_v_thumb")
                )
                self.canvas_items.append(thumb)
        
        # Горизонтальная полоса
        if direction in ['both', 'horizontal']:
            # Трек
            h_track_y1 = y2 - scrollbar_w
            h_track_x1 = x1 + 2
            h_track_x2 = x2 - (scrollbar_w + 2 if direction == 'both' else 2)
            
            track = self.canvas.create_rectangle(
                h_track_x1, h_track_y1, h_track_x2, y2 - 2,
                fill=track_color, outline='',
                tags=("element", self.id, "scroll_h_track")
            )
            self.canvas_items.append(track)
            
            # Ползунок
            track_w = h_track_x2 - h_track_x1
            view_w = x2 - x1 - (scrollbar_w if direction == 'both' else 0)
            
            if self.content_width > view_w:
                thumb_w = max(30, track_w * (view_w / self.content_width))
                thumb_x = h_track_x1 + self.scroll_x * (track_w - thumb_w)
                
                thumb = self.canvas.create_rectangle(
                    thumb_x, h_track_y1 + 2,
                    thumb_x + thumb_w, y2 - 4,
                    fill=thumb_color, outline='',
                    tags=("element", self.id, "scroll_h_thumb")
                )
                self.canvas_items.append(thumb)
        
        # Угловой квадрат (если оба направления)
        if direction == 'both':
            corner = self.canvas.create_rectangle(
                x2 - scrollbar_w, y2 - scrollbar_w,
                x2 - 2, y2 - 2,
                fill=track_color, outline='',
                tags=("element", self.id, "scroll_corner")
            )
            self.canvas_items.append(corner)

    def _draw_scroll_indicators(self, x1, y1, x2, y2):
        """Рисует индикаторы прокрутки (стрелки)"""
        direction = self.properties['scroll_direction']
        
        # Центр области
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        indicators = []
        
        if direction in ['both', 'vertical']:
            # Стрелка вверх (если можно прокрутить)
            if self.scroll_y > 0.01:
                indicators.append(('▲', cx, y1 + 20))
            # Стрелка вниз
            if self.scroll_y < 0.99:
                indicators.append(('▼', cx, y2 - 25))
        
        if direction in ['both', 'horizontal']:
            # Стрелка влево
            if self.scroll_x > 0.01:
                indicators.append(('◀', x1 + 20, cy))
            # Стрелка вправо
            if self.scroll_x < 0.99:
                indicators.append(('▶', x2 - 25, cy))
        
        for text, ix, iy in indicators:
            ind = self.canvas.create_text(
                ix, iy,
                text=text,
                font=("Arial", 12),
                fill='#555555',
                tags=("element", self.id, "scroll_indicator")
            )
            self.canvas_items.append(ind)

    def _draw_border(self, x1, y1, x2, y2):
        """Рисует рамку"""
        color = self.properties['border_color']
        width = self._scale(self.properties['border_width'])
        radius = self._scale(self.properties['corner_radius'])
        
        if width <= 0:
            return
        
        if radius > 0:
            self._draw_rounded_rect(x1, y1, x2, y2, radius, fill='', outline=color, width=width)
        else:
            border = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='', outline=color, width=width,
                tags=("element", self.id, "scroll_border")
            )
            self.canvas_items.append(border)

    # === Методы управления прокруткой ===
    
    def scroll_to(self, x=None, y=None):
        """Прокручивает к указанной позиции (0-1)"""
        if x is not None:
            self.scroll_x = max(0, min(1, x))
        if y is not None:
            self.scroll_y = max(0, min(1, y))
        self.update()

    def scroll_by(self, dx=0, dy=0):
        """Прокручивает на указанное смещение"""
        view_w = self.width - self.properties['scrollbar_width']
        view_h = self.height - self.properties['scrollbar_width']
        
        # Конвертируем пиксели в относительное смещение
        if self.content_width > view_w:
            self.scroll_x += dx / (self.content_width - view_w)
        if self.content_height > view_h:
            self.scroll_y += dy / (self.content_height - view_h)
        
        self.scroll_x = max(0, min(1, self.scroll_x))
        self.scroll_y = max(0, min(1, self.scroll_y))
        self.update()

    def scroll_to_top(self):
        """Прокручивает в начало"""
        self.scroll_y = 0
        self.update()

    def scroll_to_bottom(self):
        """Прокручивает в конец"""
        self.scroll_y = 1
        self.update()

    def scroll_to_left(self):
        """Прокручивает влево"""
        self.scroll_x = 0
        self.update()

    def scroll_to_right(self):
        """Прокручивает вправо"""
        self.scroll_x = 1
        self.update()

    def on_wheel(self, delta, horizontal=False):
        """Обработчик колеса мыши"""
        speed = self.properties['scroll_speed']
        
        if horizontal:
            self.scroll_by(dx=-delta * speed, dy=0)
        else:
            self.scroll_by(dx=0, dy=-delta * speed)

    def get_scroll_position(self):
        """Возвращает текущую позицию прокрутки"""
        return {
            'x': self.scroll_x,
            'y': self.scroll_y,
            'offset_x': self.scroll_x * max(0, self.content_width - self.width),
            'offset_y': self.scroll_y * max(0, self.content_height - self.height)
        }

    def set_content_size(self, width, height):
        """Устанавливает размер содержимого"""
        self.content_width = width
        self.content_height = height
        self.properties['content_width'] = width
        self.properties['content_height'] = height
        self.update()

    def is_point_in_v_scrollbar(self, x, y):
        """Проверяет, находится ли точка на вертикальной полосе"""
        direction = self.properties['scroll_direction']
        if direction not in ['both', 'vertical']:
            return False
        
        x1, y1, x2, y2 = self.get_screen_bounds()
        scrollbar_w = self._scale(self.properties['scrollbar_width'])
        
        return x > x2 - scrollbar_w and x < x2 and y > y1 and y < y2

    def is_point_in_h_scrollbar(self, x, y):
        """Проверяет, находится ли точка на горизонтальной полосе"""
        direction = self.properties['scroll_direction']
        if direction not in ['both', 'horizontal']:
            return False
        
        x1, y1, x2, y2 = self.get_screen_bounds()
        scrollbar_w = self._scale(self.properties['scrollbar_width'])
        
        return y > y2 - scrollbar_w and y < y2 and x > x1 and x < x2

