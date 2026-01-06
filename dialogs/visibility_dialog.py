#!/usr/bin/env python3
"""
Диалоговое окно настройки видимости элемента
Доступно через ПКМ для всех элементов
"""
import tkinter as tk
from tkinter import ttk


class VisibilityDialog:
    """Диалог настройки видимости и порядка отображения"""

    def __init__(self, parent, element, element_manager=None):
        """
        Args:
            parent: родительское окно
            element: элемент для настройки
            element_manager: менеджер элементов (для управления порядком)
        """
        self.element = element
        self.element_manager = element_manager
        self.result = None
        
        # Создаём диалоговое окно с автозакрытием
        from ..dialog_base import DialogBase
        
        self.dialog_base = DialogBase(
            parent, "Настройки отображения", 
            size_type='simple',
            auto_close=True
        )
        self.dialog = self.dialog_base.dialog
        
        self._build_ui()
        
        # Ждём закрытия
        self.dialog.wait_window()

    def _build_ui(self):
        """Создаёт интерфейс диалога"""
        # Заголовок
        elem_type = self.element.ELEMENT_TYPE if hasattr(self.element, 'ELEMENT_TYPE') else 'Элемент'
        title = tk.Label(
            self.dialog,
            text=f"👁 Настройки: {elem_type}",
            font=("Arial", 13, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        )
        title.pack(pady=(15, 15))
        
        # === Секция: Видимость ===
        vis_section = tk.LabelFrame(
            self.dialog,
            text=" Видимость ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        vis_section.pack(fill=tk.X, padx=15, pady=5)
        
        vis_frame = tk.Frame(vis_section, bg="#2a2a2a")
        vis_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Чекбокс видимости
        is_visible = self.element.is_visible if hasattr(self.element, 'is_visible') else True
        self.visible_var = tk.BooleanVar(value=is_visible)
        
        cb = tk.Checkbutton(
            vis_frame,
            text="Элемент видим",
            variable=self.visible_var,
            font=("Arial", 11),
            bg="#2a2a2a",
            fg="#ffffff",
            selectcolor="#4a4a4a",
            activebackground="#2a2a2a",
            activeforeground="#ffffff",
            command=self._on_visibility_change
        )
        cb.pack(anchor="w")
        
        # Описание
        desc = tk.Label(
            vis_frame,
            text="Скрытые элементы не отображаются на холсте,\nно сохраняются в проекте",
            font=("Arial", 9),
            bg="#2a2a2a",
            fg="#666666",
            justify=tk.LEFT
        )
        desc.pack(anchor="w", pady=(5, 0))
        
        # === Секция: Прозрачность ===
        opacity_section = tk.LabelFrame(
            self.dialog,
            text=" Прозрачность ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        opacity_section.pack(fill=tk.X, padx=15, pady=5)
        
        opacity_frame = tk.Frame(opacity_section, bg="#2a2a2a")
        opacity_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Слайдер прозрачности
        opacity = self.element.properties.get('opacity', 100) if hasattr(self.element, 'properties') else 100
        
        slider_row = tk.Frame(opacity_frame, bg="#2a2a2a")
        slider_row.pack(fill=tk.X)
        
        self.opacity_var = tk.IntVar(value=opacity)
        
        self.opacity_slider = tk.Scale(
            slider_row,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            length=180,
            bg="#2a2a2a",
            fg="#ffffff",
            troughcolor="#4a4a4a",
            highlightthickness=0,
            showvalue=False,
            sliderrelief=tk.FLAT,
            command=self._on_opacity_change
        )
        self.opacity_slider.pack(side=tk.LEFT)
        
        self.opacity_label = tk.Label(
            slider_row,
            text=f"{opacity}%",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg="#ffffff",
            width=5
        )
        self.opacity_label.pack(side=tk.LEFT, padx=10)
        
        # Быстрые значения
        quick_frame = tk.Frame(opacity_frame, bg="#2a2a2a")
        quick_frame.pack(fill=tk.X, pady=(5, 0))
        
        for val in [0, 25, 50, 75, 100]:
            btn = tk.Button(
                quick_frame,
                text=f"{val}%",
                font=("Arial", 9),
                bg="#4a4a4a",
                fg="#aaaaaa",
                activebackground="#5a5a5a",
                relief=tk.FLAT,
                width=4,
                command=lambda v=val: self._set_opacity(v)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # === Секция: Порядок слоёв ===
        order_section = tk.LabelFrame(
            self.dialog,
            text=" Порядок слоёв ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        order_section.pack(fill=tk.X, padx=15, pady=5)
        
        order_frame = tk.Frame(order_section, bg="#2a2a2a")
        order_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопки порядка
        btn_frame = tk.Frame(order_frame, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="⬆ На передний план",
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._bring_to_front
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="⬇ На задний план",
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._send_to_back
        ).pack(side=tk.LEFT, padx=2)
        
        btn_frame2 = tk.Frame(order_frame, bg="#2a2a2a")
        btn_frame2.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(
            btn_frame2,
            text="↑ Выше",
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#cccccc",
            activebackground="#4a4a4a",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._move_up
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame2,
            text="↓ Ниже",
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#cccccc",
            activebackground="#4a4a4a",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._move_down
        ).pack(side=tk.LEFT, padx=2)
        
        # === Кнопки OK/Закрыть ===
        btn_frame_main = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame_main.pack(pady=15)
        
        tk.Button(
            btn_frame_main,
            text="Закрыть",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            relief=tk.FLAT,
            padx=30,
            pady=6,
            command=self._on_close
        ).pack()
        
        # Привязка клавиш
        self.dialog.bind('<Escape>', lambda e: self._on_close())

    def _on_visibility_change(self):
        """Обработчик изменения видимости"""
        if self.visible_var.get():
            self.element.show()
        else:
            self.element.hide()

    def _on_opacity_change(self, value):
        """Обработчик изменения прозрачности"""
        opacity = int(float(value))
        self.opacity_label.config(text=f"{opacity}%")
        
        if hasattr(self.element, 'properties'):
            self.element.properties['opacity'] = opacity
            self.element.update()

    def _set_opacity(self, value):
        """Устанавливает прозрачность"""
        self.opacity_var.set(value)
        self._on_opacity_change(value)

    def _bring_to_front(self):
        """Перемещает элемент на передний план"""
        if self.element_manager:
            self.element_manager.bring_to_front(self.element)

    def _send_to_back(self):
        """Перемещает элемент на задний план"""
        if self.element_manager:
            self.element_manager.send_to_back(self.element)

    def _move_up(self):
        """Перемещает элемент на один уровень выше"""
        if self.element_manager:
            self.element_manager.move_up(self.element)

    def _move_down(self):
        """Перемещает элемент на один уровень ниже"""
        if self.element_manager:
            self.element_manager.move_down(self.element)

    def _on_close(self):
        """Закрывает диалог"""
        self.result = {
            'visible': self.visible_var.get(),
            'opacity': self.opacity_var.get()
        }
        self.dialog.destroy()


def show_visibility_dialog(parent, element, element_manager=None):
    """Показывает диалог настройки видимости"""
    dialog = VisibilityDialog(parent, element, element_manager)
    return dialog.result

