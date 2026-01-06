#!/usr/bin/env python3
"""
Инструмент выделения (Selection Tool)
Отдельный модуль для отображения рамки выделения вокруг активного элемента
Не является частью элемента - это независимый инструмент
"""


class SelectionTool:
    """Инструмент для отображения рамки выделения"""

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Текущий выбранный элемент (ссылка)
        self.selected_element = None
        
        # Canvas объекты выделения
        self.selection_items = []
        
        # Метка с размерами
        self._size_label_items = []
        self._show_size_label = False
        
        # Анимация бегущих муравьёв
        self._marching_offset = 0
        self._animation_id = None
        
        # Система масштабирования
        self.zoom_system = None

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system

    def select(self, element):
        """Выбирает элемент и показывает рамку выделения"""
        # Если тот же элемент - просто обновляем отображение
        if self.selected_element == element and element is not None:
            self.update()
            return
        
        # Сбрасываем предыдущее выделение
        if self.selected_element != element:
            self._stop_animation()
            self._clear_graphics()
        
        # Запоминаем новый элемент
        self.selected_element = element
        
        if element:
            # Запускаем анимацию
            self._start_animation()

    def deselect(self):
        """Сбрасывает выделение"""
        self._stop_animation()
        self._clear_graphics()
        self.selected_element = None

    def update(self, show_size=False):
        """Обновляет отображение выделения (при изменении элемента)"""
        self._show_size_label = show_size
        if self.selected_element:
            self._draw_selection()

    def show_size(self, show=True):
        """Включает/выключает отображение размеров"""
        self._show_size_label = show
        if self.selected_element:
            self._draw_selection()

    def _start_animation(self):
        """Запускает анимацию бегущих муравьёв"""
        self._stop_animation()
        self._animate()

    def _stop_animation(self):
        """Останавливает анимацию"""
        if self._animation_id:
            try:
                self.canvas.after_cancel(self._animation_id)
            except tk.TclError:
                pass  # Canvas destroyed
            self._animation_id = None

    def _animate(self):
        """Кадр анимации"""
        if not self.selected_element:
            return
        
        self._marching_offset = (self._marching_offset + 1) % 16
        self._draw_selection()
        
        # Следующий кадр через 50мс
        self._animation_id = self.canvas.after(50, self._animate)

    def _clear_graphics(self):
        """Удаляет графику выделения"""
        for item in self.selection_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Item already deleted
        self.selection_items = []
        
        # Удаляем метку размеров
        for item in self._size_label_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Item already deleted
        self._size_label_items = []

    def _get_element_screen_bounds(self):
        """Получает экранные границы элемента (с учётом zoom)"""
        el = self.selected_element
        if not el:
            return None
        
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(el.x, el.y)
            sw = self.zoom_system.scale_value(el.width)
            sh = self.zoom_system.scale_value(el.height)
            return (sx, sy, sx + sw, sy + sh)
        
        return (el.x, el.y, el.x + el.width, el.y + el.height)

    def _draw_selection(self):
        """Рисует рамку выделения"""
        self._clear_graphics()
        
        if not self.selected_element:
            return
        
        bounds = self._get_element_screen_bounds()
        if not bounds:
            return
        
        x1, y1, x2, y2 = bounds
        
        # Параметры пунктира
        dash_pattern = (4, 4)
        offset = self._marching_offset
        
        # Белая пунктирная рамка
        item1 = self.canvas.create_rectangle(
            x1 - 1, y1 - 1, x2 + 1, y2 + 1,
            outline="#ffffff",
            width=1,
            dash=dash_pattern,
            dashoffset=offset,
            tags=("selection_tool",)
        )
        self.selection_items.append(item1)
        
        # Чёрная пунктирная рамка (смещённая для контраста)
        item2 = self.canvas.create_rectangle(
            x1 - 1, y1 - 1, x2 + 1, y2 + 1,
            outline="#000000",
            width=1,
            dash=dash_pattern,
            dashoffset=offset + 4,
            tags=("selection_tool",)
        )
        self.selection_items.append(item2)
        
        # Маркеры resize
        self._draw_resize_handles(x1, y1, x2, y2)
        
        # Метка с размерами (если нужно показывать)
        if self._show_size_label:
            self._draw_size_label(x1, y1, x2, y2)
        
        # Поднимаем выделение наверх
        for item in self.selection_items:
            self.canvas.tag_raise(item)
        for item in self._size_label_items:
            self.canvas.tag_raise(item)

    def _draw_resize_handles(self, x1, y1, x2, y2):
        """Рисует маркеры для изменения размера"""
        marker_size = 8
        
        # Позиции маркеров (углы и середины сторон)
        handles = [
            (x1, y1),                     # nw
            (x2, y1),                     # ne
            (x1, y2),                     # sw
            (x2, y2),                     # se
            ((x1 + x2) / 2, y1),          # n
            ((x1 + x2) / 2, y2),          # s
            (x1, (y1 + y2) / 2),          # w
            (x2, (y1 + y2) / 2),          # e
        ]
        
        for hx, hy in handles:
            item = self.canvas.create_rectangle(
                hx - marker_size // 2, hy - marker_size // 2,
                hx + marker_size // 2, hy + marker_size // 2,
                fill="#ffffff",
                outline="#000000",
                width=1,
                tags=("selection_tool", "handle")
            )
            self.selection_items.append(item)

    def _draw_size_label(self, x1, y1, x2, y2):
        """Рисует метку с размерами над элементом"""
        # Очищаем предыдущую метку
        for item in self._size_label_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Item already deleted
        self._size_label_items = []
        
        if not self.selected_element:
            return
        
        # Получаем реальные размеры (не экранные)
        width = int(self.selected_element.width)
        height = int(self.selected_element.height)
        
        text = f"{width} × {height}"
        
        # Позиция над элементом (по центру)
        center_x = (x1 + x2) / 2
        label_y = y1 - 20
        
        # Ширина текста (примерная)
        text_width = len(text) * 7 + 20
        
        # Фон для метки
        bg = self.canvas.create_rectangle(
            center_x - text_width / 2, label_y - 12,
            center_x + text_width / 2, label_y + 10,
            fill="#1a1a1a",
            outline="#00aaff",
            width=1,
            tags=("size_label",)
        )
        self._size_label_items.append(bg)
        
        # Текст
        label = self.canvas.create_text(
            center_x, label_y - 1,
            text=text,
            fill="#00aaff",
            font=("Arial", 11, "bold"),
            anchor="center",
            tags=("size_label",)
        )
        self._size_label_items.append(label)

    def get_resize_handle(self, x, y):
        """Возвращает маркер resize под курсором"""
        if not self.selected_element:
            return None
        
        bounds = self._get_element_screen_bounds()
        if not bounds:
            return None
        
        x1, y1, x2, y2 = bounds
        handle_size = 10
        
        handles = {
            'nw': (x1, y1),
            'ne': (x2, y1),
            'sw': (x1, y2),
            'se': (x2, y2),
            'n': ((x1 + x2) / 2, y1),
            's': ((x1 + x2) / 2, y2),
            'w': (x1, (y1 + y2) / 2),
            'e': (x2, (y1 + y2) / 2),
        }
        
        for handle_name, (hx, hy) in handles.items():
            if abs(x - hx) <= handle_size and abs(y - hy) <= handle_size:
                return handle_name
        
        return None

    def is_active(self):
        """Проверяет, есть ли активное выделение"""
        return self.selected_element is not None


