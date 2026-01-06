#!/usr/bin/env python3
"""
Диалоговое окно настройки области прокрутки
"""
import tkinter as tk
from tkinter import ttk


class ScrollAreaConfigDialog:
    """Диалог настройки области прокрутки"""

    DIRECTIONS = [
        ('both', 'Оба направления'),
        ('vertical', 'Только вертикально'),
        ('horizontal', 'Только горизонтально'),
        ('none', 'Без прокрутки')
    ]
    
    STYLES = [
        ('auto', 'Автоматически'),
        ('always', 'Всегда видны'),
        ('hover', 'При наведении'),
        ('never', 'Скрыты')
    ]

    def __init__(self, parent, scroll_area_element):
        self.element = scroll_area_element
        self.result = None
        
        # Диалоговое окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка области прокрутки")
        self.dialog.geometry("400x520")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 520) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.configure(bg="#2a2a2a")
        
        self._build_ui()
        self.dialog.wait_window()

    def _build_ui(self):
        """Создаёт интерфейс"""
        # Заголовок
        title = tk.Label(
            self.dialog,
            text="⊞ Настройка области прокрутки",
            font=("Arial", 14, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        )
        title.pack(pady=(15, 15))
        
        # Основной контейнер
        main_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # === Направление прокрутки ===
        dir_section = self._create_section(main_frame, "Направление прокрутки")
        
        self.direction_var = tk.StringVar(value=self.element.properties['scroll_direction'])
        
        for value, label in self.DIRECTIONS:
            rb = tk.Radiobutton(
                dir_section,
                text=label,
                variable=self.direction_var,
                value=value,
                font=("Arial", 10),
                bg="#353535",
                fg="#ffffff",
                selectcolor="#4a4a4a",
                activebackground="#353535"
            )
            rb.pack(anchor="w", pady=2)
        
        # === Стиль полос прокрутки ===
        style_section = self._create_section(main_frame, "Стиль полос прокрутки")
        
        self.style_var = tk.StringVar(value=self.element.properties['scrollbar_style'])
        
        for value, label in self.STYLES:
            rb = tk.Radiobutton(
                style_section,
                text=label,
                variable=self.style_var,
                value=value,
                font=("Arial", 10),
                bg="#353535",
                fg="#ffffff",
                selectcolor="#4a4a4a",
                activebackground="#353535"
            )
            rb.pack(anchor="w", pady=2)
        
        # === Размер содержимого ===
        size_section = self._create_section(main_frame, "Размер содержимого")
        
        # Ширина
        width_row = tk.Frame(size_section, bg="#353535")
        width_row.pack(fill=tk.X, pady=4)
        
        tk.Label(width_row, text="Ширина:", font=("Arial", 10), bg="#353535", fg="#cccccc",
                width=10, anchor="w").pack(side=tk.LEFT)
        
        self.width_var = tk.IntVar(value=self.element.properties['content_width'])
        width_spin = tk.Spinbox(
            width_row,
            from_=100, to=10000,
            textvariable=self.width_var,
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            width=8
        )
        width_spin.pack(side=tk.LEFT, padx=4)
        tk.Label(width_row, text="px", font=("Arial", 9), bg="#353535", fg="#888888").pack(side=tk.LEFT)
        
        # Высота
        height_row = tk.Frame(size_section, bg="#353535")
        height_row.pack(fill=tk.X, pady=4)
        
        tk.Label(height_row, text="Высота:", font=("Arial", 10), bg="#353535", fg="#cccccc",
                width=10, anchor="w").pack(side=tk.LEFT)
        
        self.height_var = tk.IntVar(value=self.element.properties['content_height'])
        height_spin = tk.Spinbox(
            height_row,
            from_=100, to=10000,
            textvariable=self.height_var,
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            width=8
        )
        height_spin.pack(side=tk.LEFT, padx=4)
        tk.Label(height_row, text="px", font=("Arial", 9), bg="#353535", fg="#888888").pack(side=tk.LEFT)
        
        # === Поведение ===
        behavior_section = self._create_section(main_frame, "Поведение")
        
        # Скорость прокрутки
        speed_row = tk.Frame(behavior_section, bg="#353535")
        speed_row.pack(fill=tk.X, pady=4)
        
        tk.Label(speed_row, text="Скорость:", font=("Arial", 10), bg="#353535", fg="#cccccc",
                width=10, anchor="w").pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=self.element.properties['scroll_speed'])
        speed_spin = tk.Spinbox(
            speed_row,
            from_=5, to=100,
            textvariable=self.speed_var,
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            width=6
        )
        speed_spin.pack(side=tk.LEFT, padx=4)
        
        # Чекбоксы
        self.smooth_var = tk.BooleanVar(value=self.element.properties['smooth_scroll'])
        smooth_cb = tk.Checkbutton(
            behavior_section,
            text="Плавная прокрутка",
            variable=self.smooth_var,
            font=("Arial", 10),
            bg="#353535",
            fg="#ffffff",
            selectcolor="#4a4a4a"
        )
        smooth_cb.pack(anchor="w", pady=2)
        
        self.momentum_var = tk.BooleanVar(value=self.element.properties['scroll_momentum'])
        momentum_cb = tk.Checkbutton(
            behavior_section,
            text="Инерция прокрутки",
            variable=self.momentum_var,
            font=("Arial", 10),
            bg="#353535",
            fg="#ffffff",
            selectcolor="#4a4a4a"
        )
        momentum_cb.pack(anchor="w", pady=2)
        
        self.indicators_var = tk.BooleanVar(value=self.element.properties['show_scroll_indicators'])
        indicators_cb = tk.Checkbutton(
            behavior_section,
            text="Показывать индикаторы",
            variable=self.indicators_var,
            font=("Arial", 10),
            bg="#353535",
            fg="#ffffff",
            selectcolor="#4a4a4a"
        )
        indicators_cb.pack(anchor="w", pady=2)
        
        # === Кнопки ===
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="Применить",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_apply
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        # Привязка клавиш
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        self.dialog.bind('<Return>', lambda e: self._on_apply())

    def _create_section(self, parent, title):
        """Создаёт секцию"""
        section = tk.LabelFrame(
            parent,
            text=f" {title} ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        section.pack(fill=tk.X, pady=8)
        
        content = tk.Frame(section, bg="#353535")
        content.pack(fill=tk.X, padx=10, pady=8)
        
        return content

    def _on_apply(self):
        """Применяет настройки"""
        self.element.properties['scroll_direction'] = self.direction_var.get()
        self.element.properties['scrollbar_style'] = self.style_var.get()
        self.element.properties['content_width'] = self.width_var.get()
        self.element.properties['content_height'] = self.height_var.get()
        self.element.properties['scroll_speed'] = self.speed_var.get()
        self.element.properties['smooth_scroll'] = self.smooth_var.get()
        self.element.properties['scroll_momentum'] = self.momentum_var.get()
        self.element.properties['show_scroll_indicators'] = self.indicators_var.get()
        
        self.element.content_width = self.width_var.get()
        self.element.content_height = self.height_var.get()
        self.element.update()
        
        self.result = self.element.properties.copy()
        self.dialog.destroy()

    def _on_cancel(self):
        """Отменяет изменения"""
        self.dialog.destroy()


def show_scroll_area_config(parent, element):
    """Показывает диалог настройки области прокрутки"""
    dialog = ScrollAreaConfigDialog(parent, element)
    return dialog.result

