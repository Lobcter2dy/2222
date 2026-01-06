#!/usr/bin/env python3
"""
Диалоговое окно настройки рамки
Позволяет задать номер функции, точки появления и стиль
"""
import tkinter as tk
from tkinter import ttk, colorchooser


class FrameConfigDialog:
    """Диалог настройки рамки"""

    def __init__(self, parent, frame_element):
        """
        Args:
            parent: родительское окно
            frame_element: элемент рамки для настройки
        """
        self.frame_element = frame_element
        self.result = None
        
        # Точки появления (копия для редактирования)
        self.spawn_points = list(frame_element.properties.get('spawn_points', []))
        
        # Создаём диалоговое окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка рамки")
        self.dialog.geometry("400x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Стили
        self.dialog.configure(bg="#2a2a2a")
        
        self._build_ui()
        
        # Ждём закрытия
        self.dialog.wait_window()

    def _build_ui(self):
        """Создаёт интерфейс диалога"""
        # Заголовок
        title = tk.Label(
            self.dialog,
            text="⚙ Настройка рамки",
            font=("Arial", 14, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        )
        title.pack(pady=(15, 15))
        
        # === Секция: Номер функции ===
        func_section = tk.LabelFrame(
            self.dialog,
            text=" Привязка функции ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        func_section.pack(fill=tk.X, padx=15, pady=5)
        
        func_frame = tk.Frame(func_section, bg="#2a2a2a")
        func_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            func_frame,
            text="№ функции:",
            font=("Arial", 11),
            bg="#2a2a2a",
            fg="#cccccc",
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.func_id_var = tk.StringVar(
            value=str(self.frame_element.properties.get('frame_function_id', 0))
        )
        self.func_id_entry = tk.Entry(
            func_frame,
            textvariable=self.func_id_var,
            font=("Arial", 12),
            bg="#4a4a4a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            width=10
        )
        self.func_id_entry.pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        # === Секция: Стиль ===
        style_section = tk.LabelFrame(
            self.dialog,
            text=" Стиль рамки ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        style_section.pack(fill=tk.X, padx=15, pady=5)
        
        # Цвет обводки
        color_frame = tk.Frame(style_section, bg="#2a2a2a")
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(color_frame, text="Цвет:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=10, anchor="w").pack(side=tk.LEFT)
        
        self.stroke_color = self.frame_element.properties.get('stroke_color', '#ffffff')
        self.stroke_btn = tk.Button(color_frame, text="  ", width=4, bg=self.stroke_color,
                                   relief=tk.FLAT, command=self._pick_color)
        self.stroke_btn.pack(side=tk.LEFT, padx=(5, 5))
        
        self.stroke_color_var = tk.StringVar(value=self.stroke_color)
        tk.Entry(color_frame, textvariable=self.stroke_color_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=8).pack(side=tk.LEFT)
        
        # Толщина и скругление
        params_frame = tk.Frame(style_section, bg="#2a2a2a")
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(params_frame, text="Толщина:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc", width=10, anchor="w").pack(side=tk.LEFT)
        self.stroke_width_var = tk.StringVar(value=str(self.frame_element.properties.get('stroke_width', 2)))
        tk.Entry(params_frame, textvariable=self.stroke_width_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=5).pack(side=tk.LEFT, ipady=2)
        
        tk.Label(params_frame, text="Скругление:", font=("Arial", 10), bg="#2a2a2a",
                fg="#cccccc").pack(side=tk.LEFT, padx=(15, 0))
        self.radius_var = tk.StringVar(value=str(self.frame_element.properties.get('corner_radius', 0)))
        tk.Entry(params_frame, textvariable=self.radius_var, font=("Arial", 10),
                bg="#4a4a4a", fg="#ffffff", width=5).pack(side=tk.LEFT, ipady=2)
        
        # === Секция: Точки появления ===
        points_section = tk.LabelFrame(
            self.dialog,
            text=" Точки появления ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            relief=tk.GROOVE,
            borderwidth=1
        )
        points_section.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Список точек
        list_frame = tk.Frame(points_section, bg="#2a2a2a")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox с прокруткой
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.points_listbox = tk.Listbox(
            list_frame,
            bg="#3a3a3a",
            fg="#ffffff",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            font=("Consolas", 10),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#555555",
            height=6,
            yscrollcommand=scrollbar.set
        )
        self.points_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.points_listbox.yview)
        
        # Кнопки управления точками
        points_btn_frame = tk.Frame(points_section, bg="#2a2a2a")
        points_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_btn = tk.Button(
            points_btn_frame,
            text="+ Добавить",
            font=("Arial", 10),
            bg="#2d7d2d",
            fg="#ffffff",
            activebackground="#3d9d3d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._add_point
        )
        add_btn.pack(side=tk.LEFT, padx=2)
        
        edit_btn = tk.Button(
            points_btn_frame,
            text="✎ Изменить",
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._edit_point
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        del_btn = tk.Button(
            points_btn_frame,
            text="✕ Удалить",
            font=("Arial", 10),
            bg="#aa3333",
            fg="#ffffff",
            activebackground="#cc4444",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._delete_point
        )
        del_btn.pack(side=tk.LEFT, padx=2)
        
        # Поля для редактирования точки
        edit_frame = tk.Frame(points_section, bg="#2a2a2a")
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            edit_frame,
            text="X:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(side=tk.LEFT)
        
        self.point_x_var = tk.StringVar(value="0")
        self.point_x_entry = tk.Entry(
            edit_frame,
            textvariable=self.point_x_var,
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            width=6
        )
        self.point_x_entry.pack(side=tk.LEFT, padx=(5, 15), ipady=3)
        
        tk.Label(
            edit_frame,
            text="Y:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(side=tk.LEFT)
        
        self.point_y_var = tk.StringVar(value="0")
        self.point_y_entry = tk.Entry(
            edit_frame,
            textvariable=self.point_y_var,
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            width=6
        )
        self.point_y_entry.pack(side=tk.LEFT, padx=(5, 15), ipady=3)
        
        tk.Label(
            edit_frame,
            text="ID:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(side=tk.LEFT)
        
        self.point_id_var = tk.StringVar(value="1")
        self.point_id_entry = tk.Entry(
            edit_frame,
            textvariable=self.point_id_var,
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            width=4
        )
        self.point_id_entry.pack(side=tk.LEFT, padx=(5, 0), ipady=3)
        
        # Привязка выбора в списке
        self.points_listbox.bind('<<ListboxSelect>>', self._on_point_select)
        
        # Кнопки OK/Отмена
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(pady=15)
        
        ok_btn = tk.Button(
            btn_frame,
            text="Применить",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_ok
        )
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Привязка клавиш
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # Обновляем список точек
        self._update_points_list()
        
        # Фокус на поле функции
        self.func_id_entry.focus_set()
        self.func_id_entry.select_range(0, tk.END)

    def _update_points_list(self):
        """Обновляет список точек"""
        self.points_listbox.delete(0, tk.END)
        for i, point in enumerate(self.spawn_points):
            x, y = point.get('x', 0), point.get('y', 0)
            pid = point.get('id', i + 1)
            self.points_listbox.insert(tk.END, f"#{pid}  →  X: {x}, Y: {y}")

    def _on_point_select(self, event):
        """При выборе точки заполняет поля редактирования"""
        selection = self.points_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.spawn_points):
                point = self.spawn_points[index]
                self.point_x_var.set(str(point.get('x', 0)))
                self.point_y_var.set(str(point.get('y', 0)))
                self.point_id_var.set(str(point.get('id', index + 1)))

    def _add_point(self):
        """Добавляет новую точку"""
        try:
            x = int(self.point_x_var.get())
            y = int(self.point_y_var.get())
            pid = int(self.point_id_var.get())
        except ValueError:
            x, y, pid = 0, 0, len(self.spawn_points) + 1
        
        self.spawn_points.append({'x': x, 'y': y, 'id': pid})
        self._update_points_list()
        
        # Выбираем добавленную точку
        self.points_listbox.selection_clear(0, tk.END)
        self.points_listbox.selection_set(len(self.spawn_points) - 1)

    def _edit_point(self):
        """Редактирует выбранную точку"""
        selection = self.points_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.spawn_points):
            try:
                x = int(self.point_x_var.get())
                y = int(self.point_y_var.get())
                pid = int(self.point_id_var.get())
            except ValueError:
                return
            
            self.spawn_points[index] = {'x': x, 'y': y, 'id': pid}
            self._update_points_list()
            self.points_listbox.selection_set(index)

    def _delete_point(self):
        """Удаляет выбранную точку"""
        selection = self.points_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.spawn_points):
            del self.spawn_points[index]
            self._update_points_list()

    def _pick_color(self):
        """Выбор цвета обводки"""
        color = colorchooser.askcolor(color=self.stroke_color, title="Цвет обводки")
        if color[1]:
            self.stroke_color = color[1]
            self.stroke_btn.config(bg=color[1])
            self.stroke_color_var.set(color[1])

    def _on_ok(self):
        """Применяет настройки"""
        try:
            func_id = int(self.func_id_var.get())
        except ValueError:
            func_id = 0
        
        # Применяем функцию и точки
        self.frame_element.properties['frame_function_id'] = func_id
        self.frame_element.properties['spawn_points'] = self.spawn_points
        
        # Применяем стили
        self.frame_element.properties['stroke_color'] = self.stroke_color_var.get()
        try:
            self.frame_element.properties['stroke_width'] = int(self.stroke_width_var.get())
        except ValueError:
            self.frame_element.properties['stroke_width'] = 2
        try:
            self.frame_element.properties['corner_radius'] = int(self.radius_var.get())
        except ValueError:
            self.frame_element.properties['corner_radius'] = 0
        
        self.frame_element.update()
        
        # Уведомляем систему о изменении
        from ..utils.event_bus import event_bus
        event_bus.emit('element.updated', {'element': self.frame_element})
        
        self.result = {
            'function_id': func_id,
            'spawn_points': self.spawn_points
        }
        
        self.dialog.destroy()

    def _on_cancel(self):
        """Отменяет изменения"""
        self.dialog.destroy()


def show_frame_config(parent, frame_element):
    """Показывает диалог настройки рамки"""
    dialog = FrameConfigDialog(parent, frame_element)
    return dialog.result

