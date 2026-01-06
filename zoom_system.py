#!/usr/bin/env python3
"""
Система масштабирования (Zoom)
Управляет масштабом отображения без изменения реальных размеров
"""


class ZoomSystem:
    """Система масштабирования холста"""

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Текущий масштаб (1.0 = 100%)
        self.scale = 1.0
        
        # Ограничения масштаба
        self.min_scale = 0.1   # 10%
        self.max_scale = 5.0   # 500%
        
        # Шаг масштабирования
        self.zoom_step = 0.1
        
        # Точка центра масштабирования (для zoom к курсору)
        self.pivot_x = 0
        self.pivot_y = 0
        
        # Смещение viewport (для панорамирования)
        self.offset_x = 0
        self.offset_y = 0
        
        # Колбэк при изменении масштаба
        self.on_zoom_changed = None

    def set_zoom_callback(self, callback):
        """Устанавливает колбэк при изменении масштаба"""
        self.on_zoom_changed = callback

    def zoom_in(self, pivot_x=None, pivot_y=None):
        """Увеличивает масштаб"""
        new_scale = min(self.scale + self.zoom_step, self.max_scale)
        self._apply_zoom(new_scale, pivot_x, pivot_y)

    def zoom_out(self, pivot_x=None, pivot_y=None):
        """Уменьшает масштаб"""
        new_scale = max(self.scale - self.zoom_step, self.min_scale)
        self._apply_zoom(new_scale, pivot_x, pivot_y)

    def set_zoom(self, scale, pivot_x=None, pivot_y=None):
        """Устанавливает конкретный масштаб"""
        new_scale = max(self.min_scale, min(self.max_scale, scale))
        self._apply_zoom(new_scale, pivot_x, pivot_y)

    def reset_zoom(self):
        """Сбрасывает масштаб на 100%"""
        self._apply_zoom(1.0, None, None)
        self.offset_x = 0
        self.offset_y = 0

    def _apply_zoom(self, new_scale, pivot_x, pivot_y):
        """Применяет новый масштаб"""
        if new_scale == self.scale:
            return
        
        # Если указана точка pivot - масштабируем относительно неё
        if pivot_x is not None and pivot_y is not None:
            # Координаты в реальном пространстве
            real_x = self.screen_to_real_x(pivot_x)
            real_y = self.screen_to_real_y(pivot_y)
            
            # Новый масштаб
            old_scale = self.scale
            self.scale = new_scale
            
            # Корректируем смещение чтобы точка осталась на месте
            self.offset_x = pivot_x - real_x * self.scale
            self.offset_y = pivot_y - real_y * self.scale
        else:
            self.scale = new_scale
        
        # Уведомляем
        if self.on_zoom_changed:
            self.on_zoom_changed(self.scale)

    def screen_to_real_x(self, screen_x):
        """Преобразует экранную X координату в реальную"""
        return (screen_x - self.offset_x) / self.scale

    def screen_to_real_y(self, screen_y):
        """Преобразует экранную Y координату в реальную"""
        return (screen_y - self.offset_y) / self.scale

    def screen_to_real(self, screen_x, screen_y):
        """Преобразует экранные координаты в реальные"""
        return (self.screen_to_real_x(screen_x), self.screen_to_real_y(screen_y))

    def real_to_screen_x(self, real_x):
        """Преобразует реальную X координату в экранную"""
        return real_x * self.scale + self.offset_x

    def real_to_screen_y(self, real_y):
        """Преобразует реальную Y координату в экранную"""
        return real_y * self.scale + self.offset_y

    def real_to_screen(self, real_x, real_y):
        """Преобразует реальные координаты в экранные"""
        return (self.real_to_screen_x(real_x), self.real_to_screen_y(real_y))

    def scale_value(self, value):
        """Масштабирует значение (для размеров)"""
        return value * self.scale

    def unscale_value(self, value):
        """Обратное масштабирование значения"""
        return value / self.scale

    def pan(self, dx, dy):
        """Панорамирование (смещение viewport)"""
        self.offset_x += dx
        self.offset_y += dy
        
        if self.on_zoom_changed:
            self.on_zoom_changed(self.scale)

    def fit_to_element(self, element, padding=50):
        """Масштабирует чтобы элемент поместился на экране"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Вычисляем нужный масштаб
        scale_x = (canvas_width - padding * 2) / element.width
        scale_y = (canvas_height - padding * 2) / element.height
        new_scale = min(scale_x, scale_y, self.max_scale)
        new_scale = max(new_scale, self.min_scale)
        
        self.scale = new_scale
        
        # Центрируем
        self.offset_x = (canvas_width - element.width * self.scale) / 2 - element.x * self.scale
        self.offset_y = (canvas_height - element.height * self.scale) / 2 - element.y * self.scale
        
        if self.on_zoom_changed:
            self.on_zoom_changed(self.scale)

    def get_zoom_percent(self):
        """Возвращает масштаб в процентах"""
        return int(self.scale * 100)

    def apply_transform(self, x, y, width, height):
        """Применяет трансформацию к координатам и размерам"""
        return (
            self.real_to_screen_x(x),
            self.real_to_screen_y(y),
            self.scale_value(width),
            self.scale_value(height)
        )


