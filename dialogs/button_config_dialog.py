#!/usr/bin/env python3
"""
Диалоговое окно настройки кнопки
Расширенные настройки: текст, цвета, шрифт, стиль
"""
import tkinter as tk
from tkinter import ttk, colorchooser


class ButtonConfigDialog:
    """Диалог настройки кнопки"""

    def __init__(self, parent, button_element):
        """
        Args:
            parent: родительское окно
            button_element: элемент кнопки для настройки
        """
        self.button_element = button_element
        self.result = None
        
        # Создаём диалоговое окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка кнопки")
        self.dialog.geometry("420x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Стили
        self.dialog.configure(bg="#2a2a2a")
        
        # Сохраняем цвета
        self.fill_color = self.button_element.properties.get('fill_color', '#3a3a3a')
        self.stroke_color = self.button_element.properties.get('stroke_color', '#ffffff')
        self.text_color = self.button_element.properties.get('button_text_color', '#ffffff')
        self.hover_color = self.button_element.properties.get('hover_color', '#4a4a4a')
        
        self._build_ui()
        
        # Ждём закрытия
        self.dialog.wait_window()

    def _build_ui(self):
        """Создаёт интерфейс диалога"""
        # Заголовок
        tk.Label(self.dialog, text="⚙ Настройка кнопки", font=("Arial", 14, "bold"),
                bg="#2a2a2a", fg="#ffffff").pack(pady=(15, 10))
        
        # Notebook с вкладками
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # === Вкладка: Основные ===
        main_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(main_tab, text="Основные")
        self._build_main_tab(main_tab)
        
        # === Вкладка: Стиль ===
        style_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(style_tab, text="Стиль")
        self._build_style_tab(style_tab)
        
        # Кнопки OK/Отмена
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Применить", font=("Arial", 11),
                 bg="#0078d4", fg="#ffffff", relief=tk.FLAT,
                 padx=20, pady=6, command=self._on_ok).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Отмена", font=("Arial", 11),
                 bg="#4a4a4a", fg="#ffffff", relief=tk.FLAT,
                 padx=20, pady=6, command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())

    def _build_main_tab(self, parent):
        """Вкладка основных настроек"""
        # Номер функции
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(row, text="№ функции:", font=("Arial", 10), bg="#2a2a2a", 
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.func_id_var = tk.StringVar(value=str(self.button_element.get_function_id()))
        tk.Entry(row, textvariable=self.func_id_var, font=("Arial", 11),
                bg="#4a4a4a", fg="#ffffff", insertbackground="#ffffff",
                relief=tk.FLAT, width=10).pack(side=tk.LEFT, padx=(10, 0), ipady=3)
        
        # Текст кнопки
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Текст:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.text_var = tk.StringVar(value=self.button_element.properties.get('button_text', ''))
        tk.Entry(row, textvariable=self.text_var, font=("Arial", 11),
                bg="#4a4a4a", fg="#ffffff", insertbackground="#ffffff",
                relief=tk.FLAT, width=20).pack(side=tk.LEFT, padx=(10, 0), ipady=3)
        
        # Шрифт
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Шрифт:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.font_var = tk.StringVar(value=self.button_element.properties.get('button_font', 'Arial'))
        fonts = ['Arial', 'Helvetica', 'Verdana', 'Segoe UI', 'Consolas', 'Georgia']
        ttk.Combobox(row, textvariable=self.font_var, values=fonts, width=15).pack(side=tk.LEFT, padx=(10, 0))
        
        # Размер шрифта
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Размер:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.font_size_var = tk.StringVar(value=str(self.button_element.properties.get('button_font_size', 12)))
        tk.Entry(row, textvariable=self.font_size_var, font=("Arial", 11),
                bg="#4a4a4a", fg="#ffffff", insertbackground="#ffffff",
                relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=(10, 0), ipady=3)
        
        # Стиль текста
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        self.bold_var = tk.BooleanVar(value=self.button_element.properties.get('button_bold', False))
        tk.Checkbutton(row, text="Жирный", variable=self.bold_var, font=("Arial", 10),
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#4a4a4a").pack(side=tk.LEFT)
        self.italic_var = tk.BooleanVar(value=self.button_element.properties.get('button_italic', False))
        tk.Checkbutton(row, text="Курсив", variable=self.italic_var, font=("Arial", 10),
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#4a4a4a").pack(side=tk.LEFT, padx=(15, 0))

    def _build_style_tab(self, parent):
        """Вкладка стиля"""
        # Цвет заливки
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(row, text="Заливка:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.fill_btn = tk.Button(row, text="  ", width=4, bg=self.fill_color or "#3a3a3a",
                                 relief=tk.FLAT, command=self._pick_fill)
        self.fill_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.fill_var = tk.StringVar(value=self.fill_color or "")
        tk.Entry(row, textvariable=self.fill_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=10).pack(side=tk.LEFT)
        
        # Цвет обводки
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Обводка:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.stroke_btn = tk.Button(row, text="  ", width=4, bg=self.stroke_color,
                                   relief=tk.FLAT, command=self._pick_stroke)
        self.stroke_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.stroke_var = tk.StringVar(value=self.stroke_color)
        tk.Entry(row, textvariable=self.stroke_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=10).pack(side=tk.LEFT)
        
        # Цвет текста
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Цвет текста:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.text_color_btn = tk.Button(row, text="  ", width=4, bg=self.text_color,
                                       relief=tk.FLAT, command=self._pick_text_color)
        self.text_color_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.text_color_var = tk.StringVar(value=self.text_color)
        tk.Entry(row, textvariable=self.text_color_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=10).pack(side=tk.LEFT)
        
        # Цвет при наведении
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Hover:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.hover_btn = tk.Button(row, text="  ", width=4, bg=self.hover_color,
                                  relief=tk.FLAT, command=self._pick_hover)
        self.hover_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.hover_var = tk.StringVar(value=self.hover_color)
        tk.Entry(row, textvariable=self.hover_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=10).pack(side=tk.LEFT)
        
        # Толщина обводки
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Толщина:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.stroke_width_var = tk.StringVar(value=str(self.button_element.properties.get('stroke_width', 2)))
        tk.Entry(row, textvariable=self.stroke_width_var, font=("Arial", 11),
                bg="#4a4a4a", fg="#ffffff", width=6).pack(side=tk.LEFT, padx=(10, 0))
        
        # Скругление
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row, text="Скругление:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=12, anchor="w").pack(side=tk.LEFT)
        self.radius_var = tk.StringVar(value=str(self.button_element.properties.get('corner_radius', 5)))
        tk.Entry(row, textvariable=self.radius_var, font=("Arial", 11),
                bg="#4a4a4a", fg="#ffffff", width=6).pack(side=tk.LEFT, padx=(10, 0))

    def _pick_fill(self):
        color = colorchooser.askcolor(color=self.fill_color, title="Цвет заливки")
        if color[1]:
            self.fill_color = color[1]
            self.fill_btn.config(bg=color[1])
            self.fill_var.set(color[1])

    def _pick_stroke(self):
        color = colorchooser.askcolor(color=self.stroke_color, title="Цвет обводки")
        if color[1]:
            self.stroke_color = color[1]
            self.stroke_btn.config(bg=color[1])
            self.stroke_var.set(color[1])

    def _pick_text_color(self):
        color = colorchooser.askcolor(color=self.text_color, title="Цвет текста")
        if color[1]:
            self.text_color = color[1]
            self.text_color_btn.config(bg=color[1])
            self.text_color_var.set(color[1])

    def _pick_hover(self):
        color = colorchooser.askcolor(color=self.hover_color, title="Цвет при наведении")
        if color[1]:
            self.hover_color = color[1]
            self.hover_btn.config(bg=color[1])
            self.hover_var.set(color[1])

    def _on_ok(self):
        """Применяет настройки"""
        try:
            func_id = int(self.func_id_var.get())
        except ValueError:
            func_id = 0
        
        text = self.text_var.get()
        
        # Применяем к элементу
        self.button_element.set_function_id(func_id)
        self.button_element.set_button_text(text)
        
        # Стили
        props = self.button_element.properties
        props['button_font'] = self.font_var.get()
        try:
            props['button_font_size'] = int(self.font_size_var.get())
        except ValueError:
            props['button_font_size'] = 12
        props['button_bold'] = self.bold_var.get()
        props['button_italic'] = self.italic_var.get()
        props['fill_color'] = self.fill_var.get()
        props['stroke_color'] = self.stroke_var.get()
        props['button_text_color'] = self.text_color_var.get()
        props['hover_color'] = self.hover_var.get()
        try:
            props['stroke_width'] = int(self.stroke_width_var.get())
        except ValueError:
            props['stroke_width'] = 2
        try:
            props['corner_radius'] = int(self.radius_var.get())
        except ValueError:
            props['corner_radius'] = 5
        
        # Обновляем элемент
        self.button_element.update()
        
        # Уведомляем систему о изменении
        from ..utils.event_bus import event_bus
        event_bus.emit('element.updated', {'element': self.button_element})
        
        self.result = {
            'function_id': func_id,
            'text': text
        }
        
        self.dialog.destroy()

    def _on_cancel(self):
        """Отменяет изменения"""
        self.dialog.destroy()


def show_button_config(parent, button_element):
    """Показывает диалог настройки кнопки"""
    dialog = ButtonConfigDialog(parent, button_element)
    return dialog.result

