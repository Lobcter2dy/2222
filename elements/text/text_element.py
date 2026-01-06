#!/usr/bin/env python3
"""
Элемент: Текст (Text)
Позволяет размещать и стилизовать текст на холсте
"""
import tkinter as tk
from tkinter import font as tkfont
from ..element_base import ElementBase


class TextElement(ElementBase):
    """Текстовый элемент с богатыми настройками стиля"""

    ELEMENT_TYPE = "text"
    ELEMENT_SYMBOL = "T"

    # Доступные шрифты
    FONT_FAMILIES = [
        'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana',
        'Tahoma', 'Trebuchet MS', 'Courier New', 'Consolas', 'Monaco',
        'Comic Sans MS', 'Impact', 'Lucida Console', 'Palatino',
        'Garamond', 'Bookman', 'Century Gothic', 'Franklin Gothic',
        'Segoe UI', 'Roboto', 'Open Sans', 'Ubuntu', 'Liberation Sans'
    ]

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Размеры по умолчанию
        self.width = 200
        self.height = 50
        
        # Настройки текста
        self.properties.update({
            # === Основной текст ===
            'text': 'Текст',
            'text_color': '#ffffff',
            
            # === Шрифт ===
            'font_family': 'Arial',
            'font_size': 16,
            'font_weight': 'normal',      # normal, bold
            'font_style': 'roman',        # roman, italic
            'font_underline': False,
            'font_overstrike': False,
            
            # === Выравнивание ===
            'align_h': 'center',          # left, center, right
            'align_v': 'center',          # top, center, bottom
            
            # === Межстрочный интервал ===
            'line_spacing': 1.2,          # Множитель
            'letter_spacing': 0,          # Дополнительный интервал в пикселях
            'word_spacing': 0,
            
            # === Трансформация ===
            'text_transform': 'none',     # none, uppercase, lowercase, capitalize
            'rotation': 0,                # Угол поворота
            
            # === Контур текста ===
            'stroke_enabled': False,
            'stroke_color': '#000000',
            'stroke_width': 1,
            
            # === Тень текста ===
            'text_shadow': False,
            'text_shadow_x': 2,
            'text_shadow_y': 2,
            'text_shadow_color': '#000000',
            'text_shadow_blur': 0,
            
            # === Фон ===
            'background_enabled': False,
            'background_color': '#333333',
            'background_padding': 5,
            'background_radius': 0,
            
            # === Рамка вокруг текста ===
            'border_enabled': False,
            'border_color': '#ffffff',
            'border_width': 1,
            
            # === Дополнительные эффекты ===
            'opacity': 100,               # 0-100
            'blend_mode': 'normal',
            
            # === Ограничения ===
            'max_width': 0,               # 0 = без ограничения
            'wrap_text': True,            # Перенос по словам
            'ellipsis': False,            # Обрезать с "..."
        })

    def draw(self):
        """Рисует текстовый элемент"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        width = x2 - x1
        height = y2 - y1
        
        # Получаем текст с трансформацией
        text = self._transform_text(self.properties['text'])
        
        # Создаём шрифт
        font_obj = self._create_font()
        
        # Вычисляем позицию текста
        text_x, text_y, anchor = self._calculate_position(x1, y1, x2, y2)
        
        # 1. Фон текста
        if self.properties['background_enabled']:
            self._draw_background(x1, y1, x2, y2)
        
        # 2. Рамка вокруг области
        if self.properties['border_enabled']:
            self._draw_border(x1, y1, x2, y2)
        
        # 3. Тень текста
        if self.properties['text_shadow']:
            self._draw_text_shadow(text, text_x, text_y, font_obj, anchor, width)
        
        # 4. Контур текста (рисуем несколько раз со смещением)
        if self.properties['stroke_enabled'] and self.properties['stroke_width'] > 0:
            self._draw_text_stroke(text, text_x, text_y, font_obj, anchor, width)
        
        # 5. Основной текст
        text_color = self.properties['text_color']
        
        text_item = self.canvas.create_text(
            text_x, text_y,
            text=text,
            font=font_obj,
            fill=text_color,
            anchor=anchor,
            width=width if self.properties['wrap_text'] else 0,
            tags=("element", self.id, "text_main")
        )
        self.canvas_items.append(text_item)
        
        # 6. Индикатор редактирования (при выборе)
        # Рисуется selection_tool

    def _transform_text(self, text):
        """Применяет трансформацию к тексту"""
        transform = self.properties['text_transform']
        
        if transform == 'uppercase':
            return text.upper()
        elif transform == 'lowercase':
            return text.lower()
        elif transform == 'capitalize':
            return text.title()
        
        return text

    def _create_font(self):
        """Создаёт объект шрифта"""
        family = self.properties['font_family']
        size = self._scale(self.properties['font_size'])
        weight = self.properties['font_weight']
        slant = self.properties['font_style']
        underline = self.properties['font_underline']
        overstrike = self.properties['font_overstrike']
        
        return tkfont.Font(
            family=family,
            size=int(size),
            weight=weight,
            slant=slant,
            underline=underline,
            overstrike=overstrike
        )

    def _calculate_position(self, x1, y1, x2, y2):
        """Вычисляет позицию текста и якорь"""
        align_h = self.properties['align_h']
        align_v = self.properties['align_v']
        
        # Горизонтальное выравнивание
        if align_h == 'left':
            text_x = x1
            h_anchor = 'w'
        elif align_h == 'right':
            text_x = x2
            h_anchor = 'e'
        else:  # center
            text_x = (x1 + x2) / 2
            h_anchor = ''
        
        # Вертикальное выравнивание
        if align_v == 'top':
            text_y = y1
            v_anchor = 'n'
        elif align_v == 'bottom':
            text_y = y2
            v_anchor = 's'
        else:  # center
            text_y = (y1 + y2) / 2
            v_anchor = ''
        
        # Комбинируем якорь
        anchor = v_anchor + h_anchor
        if not anchor:
            anchor = 'center'
        
        return text_x, text_y, anchor

    def _draw_background(self, x1, y1, x2, y2):
        """Рисует фон текста"""
        padding = self._scale(self.properties['background_padding'])
        radius = self._scale(self.properties['background_radius'])
        color = self.properties['background_color']
        
        bx1, by1 = x1 - padding, y1 - padding
        bx2, by2 = x2 + padding, y2 + padding
        
        if radius > 0:
            # Скруглённый прямоугольник
            points = [
                bx1 + radius, by1,
                bx2 - radius, by1,
                bx2, by1,
                bx2, by1 + radius,
                bx2, by2 - radius,
                bx2, by2,
                bx2 - radius, by2,
                bx1 + radius, by2,
                bx1, by2,
                bx1, by2 - radius,
                bx1, by1 + radius,
                bx1, by1,
                bx1 + radius, by1,
            ]
            bg = self.canvas.create_polygon(
                points, smooth=True,
                fill=color, outline='',
                tags=("element", self.id, "text_bg")
            )
        else:
            bg = self.canvas.create_rectangle(
                bx1, by1, bx2, by2,
                fill=color, outline='',
                tags=("element", self.id, "text_bg")
            )
        
        self.canvas_items.append(bg)

    def _draw_border(self, x1, y1, x2, y2):
        """Рисует рамку вокруг области текста"""
        color = self.properties['border_color']
        width = self._scale(self.properties['border_width'])
        
        border = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill='', outline=color, width=width,
            tags=("element", self.id, "text_border")
        )
        self.canvas_items.append(border)

    def _draw_text_shadow(self, text, x, y, font_obj, anchor, width):
        """Рисует тень текста"""
        sx = self._scale(self.properties['text_shadow_x'])
        sy = self._scale(self.properties['text_shadow_y'])
        color = self.properties['text_shadow_color']
        
        shadow = self.canvas.create_text(
            x + sx, y + sy,
            text=text,
            font=font_obj,
            fill=color,
            anchor=anchor,
            width=width if self.properties['wrap_text'] else 0,
            tags=("element", self.id, "text_shadow")
        )
        self.canvas_items.append(shadow)

    def _draw_text_stroke(self, text, x, y, font_obj, anchor, width):
        """Рисует контур текста"""
        stroke_width = self._scale(self.properties['stroke_width'])
        stroke_color = self.properties['stroke_color']
        
        # Рисуем текст со смещением в 8 направлениях
        offsets = [
            (-stroke_width, -stroke_width),
            (0, -stroke_width),
            (stroke_width, -stroke_width),
            (-stroke_width, 0),
            (stroke_width, 0),
            (-stroke_width, stroke_width),
            (0, stroke_width),
            (stroke_width, stroke_width),
        ]
        
        for ox, oy in offsets:
            stroke = self.canvas.create_text(
                x + ox, y + oy,
                text=text,
                font=font_obj,
                fill=stroke_color,
                anchor=anchor,
                width=width if self.properties['wrap_text'] else 0,
                tags=("element", self.id, "text_stroke")
            )
            self.canvas_items.append(stroke)

    # === Методы управления текстом ===
    
    def set_text(self, text):
        """Устанавливает текст"""
        self.properties['text'] = text
        self.update()

    def get_text(self):
        """Возвращает текст"""
        return self.properties['text']

    def set_font(self, family=None, size=None, weight=None, style=None):
        """Устанавливает параметры шрифта"""
        if family is not None:
            self.properties['font_family'] = family
        if size is not None:
            self.properties['font_size'] = size
        if weight is not None:
            self.properties['font_weight'] = weight
        if style is not None:
            self.properties['font_style'] = style
        self.update()

    def set_alignment(self, horizontal=None, vertical=None):
        """Устанавливает выравнивание"""
        if horizontal is not None:
            self.properties['align_h'] = horizontal
        if vertical is not None:
            self.properties['align_v'] = vertical
        self.update()

    def enable_shadow(self, enabled=True, x=2, y=2, color='#000000'):
        """Включает/выключает тень"""
        self.properties['text_shadow'] = enabled
        self.properties['text_shadow_x'] = x
        self.properties['text_shadow_y'] = y
        self.properties['text_shadow_color'] = color
        self.update()

    def enable_stroke(self, enabled=True, width=1, color='#000000'):
        """Включает/выключает контур"""
        self.properties['stroke_enabled'] = enabled
        self.properties['stroke_width'] = width
        self.properties['stroke_color'] = color
        self.update()

    def enable_background(self, enabled=True, color='#333333', padding=5, radius=0):
        """Включает/выключает фон"""
        self.properties['background_enabled'] = enabled
        self.properties['background_color'] = color
        self.properties['background_padding'] = padding
        self.properties['background_radius'] = radius
        self.update()

    @staticmethod
    def get_available_fonts():
        """Возвращает список доступных шрифтов в системе"""
        try:
            families = list(tkfont.families())
            families.sort()
            return families
        except (tk.TclError, RuntimeError):
            return TextElement.FONT_FAMILIES

