#!/usr/bin/env python3
"""
Режим предварительного просмотра
Полноэкранный режим для тестирования интерфейса
"""
import tkinter as tk
from tkinter import ttk


class PreviewMode:
    """Управление режимом предварительного просмотра"""
    
    def __init__(self, app):
        """
        Args:
            app: Ссылка на главное приложение
        """
        self.app = app
        self.root = app.root
        self.config = app.config
        
        # Состояние
        self.is_active = False
        self.preview_window = None
        self.preview_canvas = None
        
        # Сохранённое состояние главного окна
        self.saved_geometry = None
        self.saved_state = None
        
        # Элементы в превью
        self.preview_elements = []
        self.preview_mechanisms = []
        
        # Активные таймеры (for cleanup)
        self._active_timers = []
        
        # Привязка клавиш
        self.root.bind('<F5>', self._on_f5)
        self.root.bind('<Escape>', self._on_escape)

    def start(self):
        """Запускает режим предварительного просмотра"""
        if self.is_active:
            return
        
        self.is_active = True
        
        # Сохраняем состояние
        self.saved_geometry = self.root.geometry()
        self.saved_state = self.root.state()
        
        # Создаём окно превью
        self._create_preview_window()
        
        # Копируем элементы на превью
        self._render_preview()
        
        # Запускаем механизмы
        self._start_mechanisms()
        
        print("▶ Режим просмотра запущен (ESC для выхода)")

    def stop(self):
        """Останавливает режим просмотра"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        # Отменяем все активные таймеры
        self._cancel_all_timers()
        
        # Останавливаем механизмы
        self._stop_mechanisms()
        
        # Закрываем окно превью
        if self.preview_window:
            self.preview_window.destroy()
            self.preview_window = None
            self.preview_canvas = None
        
        # Восстанавливаем главное окно
        self.root.deiconify()
        
        print("⏹ Режим просмотра завершён")
        
    def _cancel_all_timers(self):
        """Отменяет все активные таймеры"""
        for timer_id in self._active_timers:
            try:
                if self.preview_window:
                    self.preview_window.after_cancel(timer_id)
            except (tk.TclError, AttributeError):
                pass
        self._active_timers.clear()

    def toggle(self):
        """Переключает режим просмотра"""
        if self.is_active:
            self.stop()
        else:
            self.start()

    def _create_preview_window(self):
        """Создаёт полноэкранное окно превью"""
        # Скрываем главное окно
        self.root.withdraw()
        
        # Создаём новое полноэкранное окно
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Просмотр — ESC для выхода")
        
        # Полноэкранный режим
        self.preview_window.attributes('-fullscreen', True)
        self.preview_window.configure(bg='#0d1117')
        
        # Привязка клавиш в превью окне
        self.preview_window.bind('<Escape>', self._on_escape)
        self.preview_window.bind('<F5>', self._on_f5)
        self.preview_window.focus_set()
        
        # Обработка закрытия
        self.preview_window.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Создаём canvas для отображения
        self.preview_canvas = tk.Canvas(
            self.preview_window,
            bg='#0d1117',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Подсказка
        self._show_hint()
        
        # Привязка событий мыши для элементов
        self.preview_canvas.bind('<Button-1>', self._on_click)
        self.preview_canvas.bind('<Motion>', self._on_motion)

    def _show_hint(self):
        """Показывает подсказку"""
        hint_frame = tk.Frame(
            self.preview_window,
            bg='#21262d'
        )
        hint_frame.place(relx=1.0, y=10, anchor='ne', x=-10)
        
        tk.Label(
            hint_frame,
            text="ESC — выход  |  F5 — переключение",
            font=("Arial", 9),
            bg='#21262d',
            fg='#8d96a0',
            padx=10,
            pady=5
        ).pack()
        
        # Скрыть подсказку через 3 секунды
        timer_id = self.preview_window.after(3000, hint_frame.destroy)
        self._active_timers.append(timer_id)

    def _render_preview(self):
        """Отрисовывает все элементы на превью"""
        if not self.preview_canvas or not self.app.main_canvas:
            return
        
        # Получаем размеры экрана
        screen_width = self.preview_window.winfo_screenwidth()
        screen_height = self.preview_window.winfo_screenheight()
        
        # Размеры главной панели
        canvas_width = self.app.main_canvas.width
        canvas_height = self.app.main_canvas.height
        
        # Вычисляем масштаб и позицию для центрирования
        scale_x = screen_width / canvas_width
        scale_y = screen_height / canvas_height
        self.scale = min(scale_x, scale_y, 1.5)  # Максимум 150%
        
        # Позиция для центрирования
        preview_width = canvas_width * self.scale
        preview_height = canvas_height * self.scale
        self.offset_x = (screen_width - preview_width) / 2
        self.offset_y = (screen_height - preview_height) / 2
        
        # Рисуем фон главной панели
        main_color = self.app.main_canvas.properties.get('fill_color', '#000000')
        self.preview_canvas.create_rectangle(
            self.offset_x, self.offset_y,
            self.offset_x + preview_width,
            self.offset_y + preview_height,
            fill=main_color,
            outline='#30363d',
            width=1,
            tags='main_panel'
        )
        
        # Рисуем все элементы
        if self.app.element_manager:
            elements = self.app.element_manager.get_all_elements()
            for element in elements:
                self._render_element(element)

    def _render_element(self, element):
        """Отрисовывает один элемент"""
        # Позиция с учётом масштаба и смещения
        x1 = self.offset_x + element.x * self.scale
        y1 = self.offset_y + element.y * self.scale
        x2 = x1 + element.width * self.scale
        y2 = y1 + element.height * self.scale
        
        props = element.properties
        elem_type = element.ELEMENT_TYPE
        
        # Цвета
        fill_color = props.get('fill_color', '#ffffff')
        stroke_color = props.get('stroke_color', '#ffffff')
        stroke_width = props.get('stroke_width', 1) * self.scale
        
        # Тег для элемента
        tag = f"elem_{element.id}"
        
        if elem_type == 'frame':
            # Рамка (только контур)
            corner_radius = props.get('corner_radius', 0) * self.scale
            if corner_radius > 0:
                self._draw_rounded_rect(
                    x1, y1, x2, y2, corner_radius,
                    outline=stroke_color,
                    width=stroke_width,
                    fill='',
                    tags=tag
                )
            else:
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline=stroke_color,
                    width=stroke_width,
                    fill='',
                    tags=tag
                )
        
        elif elem_type == 'panel':
            # Панель (заполненная)
            corner_radius = props.get('corner_radius', 0) * self.scale
            if corner_radius > 0:
                self._draw_rounded_rect(
                    x1, y1, x2, y2, corner_radius,
                    outline=stroke_color,
                    width=stroke_width,
                    fill=fill_color,
                    tags=tag
                )
            else:
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline=stroke_color,
                    width=stroke_width,
                    fill=fill_color,
                    tags=tag
                )
        
        elif elem_type == 'button':
            # Кнопка
            corner_radius = props.get('corner_radius', 4) * self.scale
            self._draw_rounded_rect(
                x1, y1, x2, y2, corner_radius,
                outline=stroke_color,
                width=stroke_width,
                fill=fill_color,
                tags=tag
            )
            
            # Текст кнопки
            text = props.get('text', 'Кнопка')
            text_color = props.get('text_color', '#ffffff')
            font_size = int(props.get('font_size', 12) * self.scale)
            
            self.preview_canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=text,
                fill=text_color,
                font=("Arial", font_size),
                tags=tag
            )
            
            # Привязка клика для кнопки
            self.preview_canvas.tag_bind(tag, '<Button-1>', 
                lambda e, el=element: self._on_button_click(el))
            self.preview_canvas.tag_bind(tag, '<Enter>',
                lambda e, el=element: self._on_button_hover(el, True))
            self.preview_canvas.tag_bind(tag, '<Leave>',
                lambda e, el=element: self._on_button_hover(el, False))
        
        elif elem_type == 'text':
            # Текст
            text = props.get('text', 'Текст')
            text_color = props.get('text_color', props.get('fill_color', '#ffffff'))
            font_family = props.get('font_family', 'Arial')
            font_size = int(props.get('font_size', 16) * self.scale)
            
            self.preview_canvas.create_text(
                x1, y1,
                text=text,
                fill=text_color,
                font=(font_family, font_size),
                anchor='nw',
                width=(x2 - x1),
                tags=tag
            )
        
        elif elem_type == 'image':
            # Изображение (если загружено)
            if hasattr(element, 'preview_image') and element.preview_image:
                # Масштабируем изображение
                from PIL import Image, ImageTk
                img = element.original_image
                new_width = int(element.width * self.scale)
                new_height = int(element.height * self.scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                
                self.preview_canvas.create_image(
                    x1, y1,
                    image=photo,
                    anchor='nw',
                    tags=tag
                )
                
                # Сохраняем ссылку
                if not hasattr(self, '_preview_images'):
                    self._preview_images = []
                self._preview_images.append(photo)
            else:
                # Плейсхолдер
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='#2a2a2a',
                    outline='#4a4a4a',
                    tags=tag
                )
                self.preview_canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text="🖼",
                    font=("Arial", int(24 * self.scale)),
                    fill='#6a6a6a',
                    tags=tag
                )
        
        else:
            # Базовый прямоугольник для неизвестных типов
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=stroke_color,
                width=stroke_width,
                fill=fill_color,
                tags=tag
            )
        
        # Сохраняем ссылку на элемент
        self.preview_elements.append({
            'element': element,
            'tag': tag,
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
        })

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Рисует прямоугольник с закруглёнными углами"""
        tags = kwargs.pop('tags', '')
        fill = kwargs.pop('fill', '')
        outline = kwargs.pop('outline', '#ffffff')
        width = kwargs.pop('width', 1)
        
        # Упрощённая версия - используем polygon
        r = min(radius, (x2-x1)/2, (y2-y1)/2)
        
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
        ]
        
        self.preview_canvas.create_polygon(
            points,
            fill=fill,
            outline=outline,
            width=width,
            smooth=True,
            tags=tags
        )

    def _start_mechanisms(self):
        """Запускает все механизмы"""
        if not self.app.mechanism_manager:
            return
        
        mechanisms = self.app.mechanism_manager.get_all_mechanisms()
        for mech in mechanisms:
            if mech.properties.get('autostart', False):
                mech.start()
                self.preview_mechanisms.append(mech)

    def _stop_mechanisms(self):
        """Останавливает все механизмы"""
        for mech in self.preview_mechanisms:
            mech.stop()
        self.preview_mechanisms.clear()

    def _on_button_click(self, element):
        """Обработчик клика по кнопке"""
        props = element.properties
        func_id = props.get('function_id', 0)
        
        print(f"🖱 Клик по кнопке: {element.id}, функция #{func_id}")
        
        # Вызываем функцию если есть
        if hasattr(self.app, 'button_functions') and self.app.button_functions:
            self.app.button_functions.execute(func_id)
        
        # Визуальный отклик
        tag = f"elem_{element.id}"
        original_fill = props.get('fill_color', '#ffffff')
        
        # Затемняем
        self.preview_canvas.itemconfig(tag, fill='#555555')
        
        # Восстанавливаем через 100мс
        timer_id = self.preview_window.after(100, 
            lambda: self.preview_canvas.itemconfig(tag, fill=original_fill) if self.preview_canvas else None)
        self._active_timers.append(timer_id)

    def _on_button_hover(self, element, entering):
        """Обработчик наведения на кнопку"""
        tag = f"elem_{element.id}"
        props = element.properties
        
        if entering:
            # Подсветка при наведении
            hover_color = props.get('hover_color', '#4a4a4a')
            self.preview_canvas.itemconfig(tag, fill=hover_color)
            self.preview_canvas.config(cursor='hand2')
        else:
            # Возврат к исходному
            fill_color = props.get('fill_color', '#ffffff')
            self.preview_canvas.itemconfig(tag, fill=fill_color)
            self.preview_canvas.config(cursor='')

    def _on_click(self, event):
        """Общий обработчик клика"""
        pass  # Клики по элементам обрабатываются через tag_bind

    def _on_motion(self, event):
        """Обработчик движения мыши"""
        pass

    def _on_f5(self, event=None):
        """Обработчик F5"""
        self.toggle()
        return "break"

    def _on_escape(self, event=None):
        """Обработчик Escape"""
        if self.is_active:
            self.stop()
        return "break"

    def refresh(self):
        """Обновляет отображение"""
        if self.is_active and self.preview_canvas:
            self.preview_canvas.delete('all')
            self.preview_elements.clear()
            self._render_preview()

