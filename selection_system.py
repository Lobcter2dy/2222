#!/usr/bin/env python3
"""
Система выделения
Отвечает за выделение областей на холсте
"""


class SelectionSystem:
    """Управление выделением на холсте"""

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config

        self.selection_start = None
        self.selection_rect = None
        self.is_selecting = False
        self.info_label = None

        # Колбэк для обновления информации
        self.on_info_update = None

    def set_info_callback(self, callback):
        """Устанавливает колбэк для обновления информации о выделении"""
        self.on_info_update = callback

    def on_mouse_press(self, event):
        """Обработчик нажатия мыши - начало выделения"""
        self.is_selecting = True
        self.selection_start = (event.x, event.y)
        self.clear_selection()

    def on_mouse_drag(self, event):
        """Обработчик перетаскивания мыши - обновление выделения"""
        if not self.is_selecting or not self.selection_start:
            return

        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y

        # Удаляем старое выделение
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        # Создаем новое выделение
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=self.config.SELECTION_COLOR,
            width=self.config.SELECTION_WIDTH,
            tags="selection"
        )

        # Обновляем информацию
        self._update_selection_info(x1, y1, x2, y2)

    def on_mouse_release(self, event):
        """Обработчик отпускания мыши - завершение выделения"""
        self.is_selecting = False

        if self.selection_start:
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y

            # Фиксируем выделение
            self._update_selection_info(x1, y1, x2, y2)
            print(f"Выделена область: ({x1}, {y1}) -> ({x2}, {y2}), размер: {abs(x2-x1)}x{abs(y2-y1)}")

    def on_mouse_move(self, event):
        """Обработчик движения мыши - обновление координат"""
        # Вычисляем проценты от размера холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        percent_x = int((event.x / canvas_width * 100)) if canvas_width > 0 else 0
        percent_y = int((event.y / canvas_height * 100)) if canvas_height > 0 else 0

        # Вызываем колбэк
        if self.on_info_update:
            info_text = f"X:{event.x} Y:{event.y} {percent_x}%x{percent_y}%"
            self.on_info_update(info_text)

    def _update_selection_info(self, x1, y1, x2, y2):
        """Обновляет информацию о выделении"""
        # Вычисляем проценты от размера холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        percent_x1 = int((x1 / canvas_width * 100)) if canvas_width > 0 else 0
        percent_x2 = int((x2 / canvas_width * 100)) if canvas_width > 0 else 0

        # Вызываем колбэк
        if self.on_info_update:
            info_text = f"X:{x1}-{x2} Y:{y1}-{y2} {percent_x1}%-{percent_x2}%"
            self.on_info_update(info_text)

    def clear_selection(self):
        """Удаляет выделение"""
        self.canvas.delete("selection")
        self.canvas.delete("info")
        self.selection_rect = None
        self.info_label = None
        self.selection_start = None

