#!/usr/bin/env python3
"""
Расширенный диалог настройки элемента
Механизмы, текст, группировка, анимация
"""
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox


class ElementExtendedDialog:
    """Диалог расширенных настроек элемента"""

    LABEL_POSITIONS = [
        ('center', 'По центру'),
        ('top', 'Сверху'),
        ('bottom', 'Снизу'),
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('top-left', 'Сверху слева'),
        ('top-right', 'Сверху справа'),
        ('bottom-left', 'Снизу слева'),
        ('bottom-right', 'Снизу справа'),
    ]

    ANIMATION_TYPES = [
        ('none', 'Нет'),
        ('pulse', 'Пульсация'),
        ('bounce', 'Подпрыгивание'),
        ('shake', 'Тряска'),
        ('glow', 'Свечение'),
    ]

    def __init__(self, parent, element, element_manager=None, mechanism_manager=None):
        self.element = element
        self.element_manager = element_manager
        self.mechanism_manager = mechanism_manager
        self.result = None
        
        # Создаём диалог с автозакрытием
        from ..dialog_base import DialogBase
        
        self.dialog_base = DialogBase(
            parent, f"🔧 Расширенные настройки: {element.ELEMENT_TYPE}",
            size_type='large',
            resizable=True,
            auto_close=True
        )
        self.dialog = self.dialog_base.dialog
        
        self._build_ui()
        self._load_values()
        self.dialog.wait_window()

    def _build_ui(self):
        # Notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладки
        label_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(label_tab, text="📝 Текст")
        self._build_label_tab(label_tab)
        
        mechanism_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(mechanism_tab, text="⚙ Механизмы")
        self._build_mechanism_tab(mechanism_tab)
        
        group_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(group_tab, text="📦 Группа")
        self._build_group_tab(group_tab)
        
        animation_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(animation_tab, text="🎬 Анимация")
        self._build_animation_tab(animation_tab)
        
        transform_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(transform_tab, text="🔄 Трансформ")
        self._build_transform_tab(transform_tab)
        
        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="Применить", font=("Arial", 10), bg="#0078d4", fg="#ffffff",
                 relief=tk.FLAT, padx=20, pady=6, command=self._on_apply).pack(side=tk.LEFT)
        
        tk.Button(btn_frame, text="Отмена", font=("Arial", 10), bg="#4a4a4a", fg="#ffffff",
                 relief=tk.FLAT, padx=20, pady=6, command=self._on_cancel).pack(side=tk.LEFT, padx=10)

    def _build_label_tab(self, parent):
        """Вкладка текстовой подписи"""
        # Включить подпись
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        self.label_enabled_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Включить текстовую подпись", variable=self.label_enabled_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a",
                      font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Текст
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Текст:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.label_text_var = tk.StringVar()
        tk.Entry(row, textvariable=self.label_text_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=30).pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        # Шрифт и размер
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Шрифт:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.label_font_var = tk.StringVar()
        fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia', 'Impact']
        font_combo = ttk.Combobox(row, textvariable=self.label_font_var, values=fonts, width=15)
        font_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(row, text="Размер:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.label_size_var = tk.StringVar()
        tk.Entry(row, textvariable=self.label_size_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=5).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        # Стиль
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        self.label_bold_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Жирный", variable=self.label_bold_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.label_italic_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Курсив", variable=self.label_italic_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(row, text="Цвет:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.label_color_btn = tk.Button(row, text="  ", bg="#ffffff", width=4, relief=tk.FLAT,
                                        command=self._pick_label_color)
        self.label_color_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.label_color_var = "#ffffff"
        
        # Позиция
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Позиция:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.label_position_var = tk.StringVar()
        pos_combo = ttk.Combobox(row, textvariable=self.label_position_var, state="readonly", width=15)
        pos_combo['values'] = [p[1] for p in self.LABEL_POSITIONS]
        pos_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Смещение
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Смещение X:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.label_offset_x_var = tk.StringVar()
        tk.Entry(row, textvariable=self.label_offset_x_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        tk.Label(row, text="Y:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(15, 0))
        self.label_offset_y_var = tk.StringVar()
        tk.Entry(row, textvariable=self.label_offset_y_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=(5, 0), ipady=4)

    def _build_mechanism_tab(self, parent):
        """Вкладка механизмов"""
        info = tk.Label(parent, text="Привяжите механизмы к элементу для создания интерактивности",
                       bg="#2a2a2a", fg="#888888", font=("Arial", 9))
        info.pack(pady=(10, 5))
        
        # Два списка
        lists_frame = tk.Frame(parent, bg="#2a2a2a")
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Доступные механизмы
        left_frame = tk.Frame(lists_frame, bg="#2a2a2a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="Доступные механизмы:", bg="#2a2a2a", fg="#888888", font=("Arial", 9)).pack(anchor="w")
        
        self.available_mech_listbox = tk.Listbox(left_frame, bg="#3a3a3a", fg="#ffffff",
                                                selectbackground="#0078d4", font=("Arial", 10), height=10)
        self.available_mech_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(left_frame, text="▶ Привязать", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._attach_mechanism).pack()
        
        # Привязанные механизмы
        right_frame = tk.Frame(lists_frame, bg="#2a2a2a")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="Привязанные:", bg="#2a2a2a", fg="#4aff4a", font=("Arial", 9)).pack(anchor="w")
        
        self.attached_mech_listbox = tk.Listbox(right_frame, bg="#3a3a3a", fg="#4aff4a",
                                               selectbackground="#0078d4", font=("Arial", 10), height=10)
        self.attached_mech_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(right_frame, text="◀ Отвязать", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._detach_mechanism).pack()
        
        # Кнопки управления
        ctrl_frame = tk.Frame(parent, bg="#2a2a2a")
        ctrl_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Button(ctrl_frame, text="▶ Запустить все", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, padx=10, command=self._start_all_mechanisms).pack(side=tk.LEFT, padx=2)
        
        tk.Button(ctrl_frame, text="⏹ Остановить все", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, padx=10, command=self._stop_all_mechanisms).pack(side=tk.LEFT, padx=2)

    def _build_group_tab(self, parent):
        """Вкладка группировки"""
        # Информация о родителе
        parent_frame = tk.LabelFrame(parent, text=" Родительский элемент ", bg="#2a2a2a", fg="#888888")
        parent_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        self.parent_label = tk.Label(parent_frame, text="Нет родителя", bg="#2a2a2a", fg="#ffffff", font=("Arial", 10))
        self.parent_label.pack(padx=10, pady=10, anchor="w")
        
        btn_row = tk.Frame(parent_frame, bg="#2a2a2a")
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(btn_row, text="Отсоединить от родителя", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._detach_from_parent).pack(side=tk.LEFT)
        
        # Дочерние элементы
        children_frame = tk.LabelFrame(parent, text=" Дочерние элементы ", bg="#2a2a2a", fg="#888888")
        children_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Списки
        lists_frame = tk.Frame(children_frame, bg="#2a2a2a")
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Доступные
        left = tk.Frame(lists_frame, bg="#2a2a2a")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left, text="Доступные:", bg="#2a2a2a", fg="#888888", font=("Arial", 9)).pack(anchor="w")
        self.available_children_listbox = tk.Listbox(left, bg="#3a3a3a", fg="#ffffff",
                                                    selectbackground="#0078d4", font=("Arial", 9), height=6)
        self.available_children_listbox.pack(fill=tk.BOTH, expand=True, pady=3)
        
        tk.Button(left, text="▶ Добавить в группу", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._add_child).pack()
        
        # Дочерние
        right = tk.Frame(lists_frame, bg="#2a2a2a")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right, text="В группе:", bg="#2a2a2a", fg="#4affff", font=("Arial", 9)).pack(anchor="w")
        self.children_listbox = tk.Listbox(right, bg="#3a3a3a", fg="#4affff",
                                          selectbackground="#0078d4", font=("Arial", 9), height=6)
        self.children_listbox.pack(fill=tk.BOTH, expand=True, pady=3)
        
        tk.Button(right, text="◀ Убрать из группы", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._remove_child).pack()

    def _build_animation_tab(self, parent):
        """Вкладка анимации"""
        # Включить анимацию
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        self.anim_enabled_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Включить анимацию", variable=self.anim_enabled_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Тип анимации
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Тип анимации:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.anim_type_var = tk.StringVar()
        anim_combo = ttk.Combobox(row, textvariable=self.anim_type_var, state="readonly", width=20)
        anim_combo['values'] = [a[1] for a in self.ANIMATION_TYPES]
        anim_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Скорость
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Скорость:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.anim_speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(row, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
                              variable=self.anim_speed_var, bg="#2a2a2a", fg="#ffffff",
                              troughcolor="#3a3a3a", highlightthickness=0, length=200)
        speed_scale.pack(side=tk.LEFT, padx=(10, 0))
        
        # Зацикливание
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        self.anim_loop_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row, text="Зацикливать анимацию", variable=self.anim_loop_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Кнопки
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(row, text="▶ Запустить", font=("Arial", 10), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, padx=15, command=self._start_animation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(row, text="⏹ Остановить", font=("Arial", 10), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, padx=15, command=self._stop_animation).pack(side=tk.LEFT, padx=5)

    def _build_transform_tab(self, parent):
        """Вкладка трансформаций"""
        # Поворот
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(row, text="Поворот (°):", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.rotation_var = tk.StringVar()
        tk.Entry(row, textvariable=self.rotation_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        # Масштаб
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Масштаб X:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.scale_x_var = tk.StringVar()
        tk.Entry(row, textvariable=self.scale_x_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        tk.Label(row, text="Y:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(15, 0))
        self.scale_y_var = tk.StringVar()
        tk.Entry(row, textvariable=self.scale_y_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        # Отражение
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        self.flip_h_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Отразить по горизонтали", variable=self.flip_h_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.flip_v_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Отразить по вертикали", variable=self.flip_v_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT, padx=(15, 0))
        
        # Блокировки
        lock_frame = tk.LabelFrame(parent, text=" Блокировки ", bg="#2a2a2a", fg="#888888")
        lock_frame.pack(fill=tk.X, padx=15, pady=15)
        
        row = tk.Frame(lock_frame, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=10, pady=10)
        
        self.size_locked_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Заблокировать размер", variable=self.size_locked_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.position_locked_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Заблокировать позицию", variable=self.position_locked_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a", font=("Arial", 10)).pack(side=tk.LEFT, padx=(15, 0))

    def _load_values(self):
        """Загружает текущие значения"""
        props = self.element.properties
        
        # Текст
        self.label_enabled_var.set(props.get('label_enabled', False))
        self.label_text_var.set(props.get('label_text', ''))
        self.label_font_var.set(props.get('label_font', 'Arial'))
        self.label_size_var.set(str(props.get('label_size', 12)))
        self.label_bold_var.set(props.get('label_bold', False))
        self.label_italic_var.set(props.get('label_italic', False))
        self.label_color_var = props.get('label_color', '#ffffff')
        self.label_color_btn.configure(bg=self.label_color_var)
        
        pos = props.get('label_position', 'center')
        for code, name in self.LABEL_POSITIONS:
            if code == pos:
                self.label_position_var.set(name)
                break
        
        self.label_offset_x_var.set(str(props.get('label_offset_x', 0)))
        self.label_offset_y_var.set(str(props.get('label_offset_y', 0)))
        
        # Анимация
        self.anim_enabled_var.set(props.get('animation_enabled', False))
        anim_type = props.get('animation_type', 'none')
        for code, name in self.ANIMATION_TYPES:
            if code == anim_type:
                self.anim_type_var.set(name)
                break
        self.anim_speed_var.set(props.get('animation_speed', 1.0))
        self.anim_loop_var.set(props.get('animation_loop', True))
        
        # Трансформации
        self.rotation_var.set(str(props.get('rotation', 0)))
        self.scale_x_var.set(str(props.get('scale_x', 1.0)))
        self.scale_y_var.set(str(props.get('scale_y', 1.0)))
        self.flip_h_var.set(props.get('flip_h', False))
        self.flip_v_var.set(props.get('flip_v', False))
        
        # Блокировки
        self.size_locked_var.set(self.element.size_locked)
        self.position_locked_var.set(self.element.position_locked)
        
        # Обновляем списки
        self._refresh_mechanism_lists()
        self._refresh_group_lists()

    def _refresh_mechanism_lists(self):
        """Обновляет списки механизмов"""
        self.available_mech_listbox.delete(0, tk.END)
        self.attached_mech_listbox.delete(0, tk.END)
        
        if not self.mechanism_manager:
            return
        
        for mech in self.mechanism_manager.get_all_mechanisms():
            mech_name = f"{mech.MECHANISM_TYPE}: {mech.id[:10]}"
            
            if mech.id in self.element.attached_mechanisms:
                self.attached_mech_listbox.insert(tk.END, mech_name)
            else:
                self.available_mech_listbox.insert(tk.END, mech_name)

    def _refresh_group_lists(self):
        """Обновляет списки группы"""
        self.available_children_listbox.delete(0, tk.END)
        self.children_listbox.delete(0, tk.END)
        
        # Родитель
        if self.element.parent_group and self.element_manager:
            parent = self.element_manager.get_element_by_id(self.element.parent_group)
            if parent:
                self.parent_label.config(text=f"{parent.ELEMENT_TYPE}: {parent.id[:10]}")
            else:
                self.parent_label.config(text="Нет родителя")
        else:
            self.parent_label.config(text="Нет родителя")
        
        if not self.element_manager:
            return
        
        for elem in self.element_manager.get_all_elements():
            if elem.id == self.element.id:
                continue
            if elem.parent_group:
                continue  # Уже в другой группе
            
            elem_name = f"{elem.ELEMENT_TYPE}: {elem.id[:10]}"
            
            if elem.id in self.element.children:
                self.children_listbox.insert(tk.END, elem_name)
            else:
                self.available_children_listbox.insert(tk.END, elem_name)

    def _pick_label_color(self):
        color = colorchooser.askcolor(color=self.label_color_var, title="Цвет текста")
        if color[1]:
            self.label_color_var = color[1]
            self.label_color_btn.configure(bg=color[1])

    def _attach_mechanism(self):
        sel = self.available_mech_listbox.curselection()
        if not sel:
            return
        
        text = self.available_mech_listbox.get(sel[0])
        mech_id_part = text.split(": ")[1]
        
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                if mech.id.startswith(mech_id_part):
                    self.element.attach_mechanism(mech.id)
                    break
        
        self._refresh_mechanism_lists()

    def _detach_mechanism(self):
        sel = self.attached_mech_listbox.curselection()
        if not sel:
            return
        
        text = self.attached_mech_listbox.get(sel[0])
        mech_id_part = text.split(": ")[1]
        
        for mech_id in self.element.attached_mechanisms:
            if mech_id.startswith(mech_id_part):
                self.element.detach_mechanism(mech_id)
                break
        
        self._refresh_mechanism_lists()

    def _start_all_mechanisms(self):
        self.element.start_all_mechanisms()
        messagebox.showinfo("Механизмы", "Все механизмы запущены!")

    def _stop_all_mechanisms(self):
        self.element.stop_all_mechanisms()
        messagebox.showinfo("Механизмы", "Все механизмы остановлены!")

    def _detach_from_parent(self):
        if self.element.parent_group and self.element_manager:
            parent = self.element_manager.get_element_by_id(self.element.parent_group)
            if parent:
                parent.remove_child(self.element.id)
        self._refresh_group_lists()

    def _add_child(self):
        sel = self.available_children_listbox.curselection()
        if not sel:
            return
        
        text = self.available_children_listbox.get(sel[0])
        elem_id_part = text.split(": ")[1]
        
        if self.element_manager:
            for elem in self.element_manager.get_all_elements():
                if elem.id.startswith(elem_id_part):
                    self.element.add_child(elem.id)
                    break
        
        self._refresh_group_lists()

    def _remove_child(self):
        sel = self.children_listbox.curselection()
        if not sel:
            return
        
        text = self.children_listbox.get(sel[0])
        elem_id_part = text.split(": ")[1]
        
        for child_id in self.element.children:
            if child_id.startswith(elem_id_part):
                self.element.remove_child(child_id)
                break
        
        self._refresh_group_lists()

    def _start_animation(self):
        anim_name = self.anim_type_var.get()
        for code, name in self.ANIMATION_TYPES:
            if name == anim_name:
                self.element.start_animation(code)
                break

    def _stop_animation(self):
        self.element.stop_animation()

    def _on_apply(self):
        props = self.element.properties
        
        # Текст
        props['label_enabled'] = self.label_enabled_var.get()
        props['label_text'] = self.label_text_var.get()
        props['label_font'] = self.label_font_var.get()
        try:
            props['label_size'] = int(self.label_size_var.get())
        except ValueError:
            pass  # Invalid number, keep default
        props['label_bold'] = self.label_bold_var.get()
        props['label_italic'] = self.label_italic_var.get()
        props['label_color'] = self.label_color_var
        
        pos_name = self.label_position_var.get()
        for code, name in self.LABEL_POSITIONS:
            if name == pos_name:
                props['label_position'] = code
                break
        
        try:
            props['label_offset_x'] = int(self.label_offset_x_var.get())
            props['label_offset_y'] = int(self.label_offset_y_var.get())
        except ValueError:
            pass  # Invalid number, keep default
        
        # Анимация
        props['animation_enabled'] = self.anim_enabled_var.get()
        anim_name = self.anim_type_var.get()
        for code, name in self.ANIMATION_TYPES:
            if name == anim_name:
                props['animation_type'] = code
                break
        props['animation_speed'] = self.anim_speed_var.get()
        props['animation_loop'] = self.anim_loop_var.get()
        
        # Трансформации
        try:
            props['rotation'] = float(self.rotation_var.get())
            props['scale_x'] = float(self.scale_x_var.get())
            props['scale_y'] = float(self.scale_y_var.get())
        except ValueError:
            pass  # Invalid number, keep default
        props['flip_h'] = self.flip_h_var.get()
        props['flip_v'] = self.flip_v_var.get()
        
        # Блокировки
        self.element.size_locked = self.size_locked_var.get()
        self.element.position_locked = self.position_locked_var.get()
        
        self.element.update()
        self.result = True
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


def show_element_extended_dialog(parent, element, element_manager=None, mechanism_manager=None):
    """Показывает расширенный диалог настройки элемента"""
    dialog = ElementExtendedDialog(parent, element, element_manager, mechanism_manager)
    return dialog.result

