#!/usr/bin/env python3
"""
Элемент: Изображение (Image)
Позволяет загрузить и отобразить изображение на холсте
"""
from ..element_base import ElementBase
from tkinter import filedialog
import os

# Пробуем импортировать PIL для работы с изображениями
PIL_AVAILABLE = False
Image = None
ImageTk = None

try:
    from PIL import Image as PILImage
    from PIL import ImageTk as PILImageTk
    Image = PILImage
    ImageTk = PILImageTk
    PIL_AVAILABLE = True
except ImportError:
    pass


class ImageElement(ElementBase):
    """Изображение - элемент для отображения картинок"""

    ELEMENT_TYPE = "image"
    ELEMENT_SYMBOL = "🖼"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Настройки по умолчанию для изображения
        self.properties.update({
            'fill_color': '#2a2a2a',      # Фон-заглушка
            'stroke_color': '#5a5a5a',
            'stroke_width': 1,
            'display_mode': 'both',
            
            # Специфичные для изображения
            'image_path': '',              # Путь к файлу
            'image_fit': 'contain',        # contain, cover, stretch, original
            'image_opacity': 1.0,          # Прозрачность
        })
        
        # Кеш загруженного изображения
        self._original_image = None     # PIL Image
        self._display_image = None      # ImageTk.PhotoImage
        self._image_item = None         # Canvas item ID

    def draw(self):
        """Рисует изображение"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Получаем свойства
        stroke_color = self.properties['stroke_color']
        stroke_width = self._scale(self.properties['stroke_width'])
        fill_color = self.properties['fill_color'] or '#2a2a2a'
        display_mode = self.properties['display_mode']
        
        draw_fill = display_mode in ('fill', 'both')
        draw_stroke = display_mode in ('stroke', 'both') and stroke_color
        stroke_width = max(1, stroke_width) if draw_stroke else 0

        # 1. Тень
        if self.properties['shadow_enabled']:
            self._draw_shadow(x1, y1, x2, y2)

        # 2. Фон (если нет изображения или как подложка)
        bg = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=fill_color if draw_fill else '',
            outline=stroke_color if draw_stroke else '',
            width=stroke_width,
            tags=("element", self.id, "background")
        )
        self.canvas_items.append(bg)

        # 3. Изображение
        if self.properties['image_path'] and PIL_AVAILABLE:
            self._draw_image(x1, y1, x2, y2)
        elif not self.properties['image_path']:
            # Рисуем placeholder
            self._draw_placeholder(x1, y1, x2, y2)

        # 4. Рамка поверх
        if draw_stroke:
            border = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='',
                outline=stroke_color,
                width=stroke_width,
                tags=("element", self.id, "border")
            )
            self.canvas_items.append(border)

    def _draw_shadow(self, x1, y1, x2, y2):
        """Рисует тень"""
        sx = self._scale(self.properties['shadow_x'])
        sy = self._scale(self.properties['shadow_y'])
        color = self.properties['shadow_color']
        
        shadow = self.canvas.create_rectangle(
            x1 + sx, y1 + sy, x2 + sx, y2 + sy,
            fill=color, outline='',
            tags=("element", self.id, "shadow")
        )
        self.canvas_items.append(shadow)

    def _draw_placeholder(self, x1, y1, x2, y2):
        """Рисует заглушку когда изображение не загружено"""
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Крест по диагоналям
        line1 = self.canvas.create_line(
            x1 + 10, y1 + 10, x2 - 10, y2 - 10,
            fill="#555555", width=1, dash=(4, 4),
            tags=("element", self.id, "placeholder")
        )
        self.canvas_items.append(line1)
        
        line2 = self.canvas.create_line(
            x2 - 10, y1 + 10, x1 + 10, y2 - 10,
            fill="#555555", width=1, dash=(4, 4),
            tags=("element", self.id, "placeholder")
        )
        self.canvas_items.append(line2)
        
        # Иконка изображения
        icon = self.canvas.create_text(
            center_x, center_y,
            text="🖼",
            fill="#666666",
            font=("Arial", 24),
            anchor="center",
            tags=("element", self.id, "placeholder")
        )
        self.canvas_items.append(icon)
        
        # Текст подсказки
        hint = self.canvas.create_text(
            center_x, center_y + 30,
            text="ПКМ → Загрузить",
            fill="#555555",
            font=("Arial", 9),
            anchor="center",
            tags=("element", self.id, "placeholder")
        )
        self.canvas_items.append(hint)

    def _draw_image(self, x1, y1, x2, y2):
        """Рисует загруженное изображение"""
        if not PIL_AVAILABLE:
            return
        
        try:
            # Загружаем изображение если ещё не загружено
            if self._original_image is None:
                self._load_image()
            
            if self._original_image is None:
                return
            
            # Размеры области
            width = int(x2 - x1)
            height = int(y2 - y1)
            
            if width <= 0 or height <= 0:
                return
            
            # Масштабируем изображение по fit режиму
            resized = self._resize_image(width, height)
            
            if resized is None:
                return
            
            # Создаём PhotoImage
            self._display_image = ImageTk.PhotoImage(resized)
            
            # Вычисляем позицию (центрируем)
            img_width = resized.width
            img_height = resized.height
            img_x = x1 + (width - img_width) / 2
            img_y = y1 + (height - img_height) / 2
            
            # Создаём на canvas
            self._image_item = self.canvas.create_image(
                img_x, img_y,
                image=self._display_image,
                anchor="nw",
                tags=("element", self.id, "image")
            )
            self.canvas_items.append(self._image_item)
            
        except Exception as e:
            print(f"[ImageElement] Ошибка отрисовки: {e}")

    def _load_image(self):
        """Загружает изображение из файла"""
        if not PIL_AVAILABLE:
            return
        
        path = self.properties.get('image_path', '')
        if not path or not os.path.exists(path):
            self._original_image = None
            return
        
        try:
            self._original_image = Image.open(path)
            # Конвертируем в RGBA для поддержки прозрачности
            if self._original_image.mode != 'RGBA':
                self._original_image = self._original_image.convert('RGBA')
        except Exception as e:
            print(f"[ImageElement] Ошибка загрузки {path}: {e}")
            self._original_image = None

    def _resize_image(self, target_width, target_height):
        """Масштабирует изображение согласно fit режиму"""
        if self._original_image is None:
            return None
        
        orig_width, orig_height = self._original_image.size
        fit_mode = self.properties.get('image_fit', 'contain')
        
        if fit_mode == 'original':
            # Без масштабирования
            return self._original_image.copy()
        
        elif fit_mode == 'stretch':
            # Растянуть до размеров области
            return self._original_image.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS
            )
        
        elif fit_mode == 'cover':
            # Покрыть всю область (с обрезкой)
            ratio_w = target_width / orig_width
            ratio_h = target_height / orig_height
            ratio = max(ratio_w, ratio_h)
            
            new_w = int(orig_width * ratio)
            new_h = int(orig_height * ratio)
            
            resized = self._original_image.resize(
                (new_w, new_h),
                Image.Resampling.LANCZOS
            )
            
            # Обрезаем по центру
            left = (new_w - target_width) // 2
            top = (new_h - target_height) // 2
            return resized.crop((left, top, left + target_width, top + target_height))
        
        else:  # contain (по умолчанию)
            # Вписать в область сохраняя пропорции
            ratio_w = target_width / orig_width
            ratio_h = target_height / orig_height
            ratio = min(ratio_w, ratio_h)
            
            new_w = int(orig_width * ratio)
            new_h = int(orig_height * ratio)
            
            return self._original_image.resize(
                (new_w, new_h),
                Image.Resampling.LANCZOS
            )

    def load_image_dialog(self):
        """Открывает диалог выбора изображения"""
        filetypes = [
            ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("GIF", "*.gif"),
            ("BMP", "*.bmp"),
            ("WebP", "*.webp"),
            ("Все файлы", "*.*")
        ]
        
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=filetypes
        )
        
        if path:
            self.set_image(path)
            return path
        return None

    def set_image(self, path):
        """Устанавливает изображение по пути"""
        self.properties['image_path'] = path
        self._original_image = None  # Сбрасываем кеш
        self._display_image = None
        self.update()

    def clear_image(self):
        """Очищает изображение"""
        self.properties['image_path'] = ''
        self._original_image = None
        self._display_image = None
        self.update()

    def get_image_path(self):
        """Возвращает путь к изображению"""
        return self.properties.get('image_path', '')

    def set_fit_mode(self, mode):
        """Устанавливает режим масштабирования"""
        if mode in ('contain', 'cover', 'stretch', 'original'):
            self.properties['image_fit'] = mode
            self._display_image = None  # Пересчитать
            self.update()

