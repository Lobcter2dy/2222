#!/usr/bin/env python3
"""
Вкладка элементов - создание и управление элементами интерфейса
"""
import tkinter as tk
from tkinter import ttk
from .tab_base import TabBase


class TabElements(TabBase):
    """Вкладка управления элементами"""

    TAB_ID = "elements"
    TAB_SYMBOL = "▢"

    ELEMENTS = [
        ('frame', '□', 'Рамка'),
        ('panel', '▢', 'Панель'),
        ('button', '⬚', 'Кнопка'),
        ('image', '▣', 'Изображение'),
        ('text', 'T', 'Текст'),
        ('scroll_area', '⊞', 'Скролл'),
        ('state_switcher', '◇', 'Состояния'),
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.element_manager = None
        self.artifact_manager = None
        self.btns = {}
        self.artifact_btns = {}
        self.artifact_element_btns = {}
        self.selected_artifact = None
        self._updating = False  # Защита от рекурсии
        
        # Ссылки на frames (инициализируются в _build_content)
        self.artifacts_frame = None
        self.artifact_elements_frame = None
        self.artifact_info_lbl = None
        
        # Для рисования артефактов
        self._pending_artifact_id = None
        self._artifact_draw_start = None
        self._artifact_preview_rect = None
        self._app = None  # Ссылка на приложение
        
        # Для артефактов
        self.artifact_manager_integrated = None
        self._pending_artifact_type = None

    def set_element_manager(self, manager):
        self.element_manager = manager
        if manager:
            manager.set_selection_callback(self._on_selection)
    
    def set_app(self, app):
        """Устанавливает ссылку на приложение для восстановления обработчиков"""
        self._app = app
    
    def set_artifact_manager(self, manager):
        """Устанавливает менеджер артефактов"""
        self.artifact_manager = manager
        if manager:
            manager.set_selection_callback(self._on_artifact_selected)
            self._refresh_artifacts()

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Создание ===
        sec = self._section(self.content, "Создать элемент")
        
        grid = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        grid.pack(fill=tk.X)
        
        for i, (etype, sym, name) in enumerate(self.ELEMENTS):
            btn = tk.Button(grid, text=sym, font=("Arial", 14),
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                           activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                           relief=tk.FLAT, width=3, height=1, cursor="hand2",
                           command=lambda t=etype: self._create(t))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="ew")
            self._tooltip(btn, name)
            self.btns[etype] = btn
        
        for c in range(4):
            grid.columnconfigure(c, weight=1)
        
        self.status_lbl = tk.Label(sec, text="", font=("Arial", 9),
                                  bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_ACCENT)
        self.status_lbl.pack(anchor="w", pady=(4, 0))
        
        # === Артефакты (заготовки) ===
        self._build_artifacts_section()
        
        # === Список ===
        sec = self._section(self.content, "На холсте")
        
        # Тулбар
        toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        
        for sym, tip, cmd in [('▲', 'Вверх', self._up), ('▼', 'Вниз', self._down),
                              ('⧉', 'Копировать', self._copy), ('✕', 'Удалить', self._delete)]:
            b = self._icon_button(toolbar, sym, cmd)
            b.pack(side=tk.LEFT, padx=1)
            self._tooltip(b, tip)
        
        self._icon_button(toolbar, '⟳', self._refresh).pack(side=tk.RIGHT, padx=1)
        
        # Список
        cols = ('type', 'name', 'size')
        self.tree = self._tree(sec, cols, 8)
        self.tree.heading('type', text='')
        self.tree.heading('name', text='Элемент')
        self.tree.heading('size', text='Размер')
        self.tree.column('type', width=30)
        self.tree.column('name', width=100)
        self.tree.column('size', width=70)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # НЕ привязываем <<TreeviewSelect>> - вызывает бесконечный цикл
        self.tree.bind('<ButtonRelease-1>', self._on_tree_click)
        
        # === Свойства ===
        sec = self._section(self.content, "Свойства")
        
        # Тип
        row = self._row(sec)
        self._label(row, "Тип:").pack(side=tk.LEFT)
        self.prop_type = tk.Label(row, text="—", font=("Arial", 9, "bold"),
                                 bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT)
        self.prop_type.pack(side=tk.LEFT)
        
        # Позиция
        row = self._row(sec)
        self._label(row, "X:").pack(side=tk.LEFT)
        self.prop_x = tk.StringVar(value="0")
        self._entry(row, self.prop_x, 5).pack(side=tk.LEFT)
        self._label(row, "Y:", 3).pack(side=tk.LEFT, padx=(8, 0))
        self.prop_y = tk.StringVar(value="0")
        self._entry(row, self.prop_y, 5).pack(side=tk.LEFT)
        
        # Размер
        row = self._row(sec)
        self._label(row, "Ширина:").pack(side=tk.LEFT)
        self.prop_w = tk.StringVar(value="100")
        self._entry(row, self.prop_w, 5).pack(side=tk.LEFT)
        self._label(row, "Высота:", 7).pack(side=tk.LEFT, padx=(8, 0))
        self.prop_h = tk.StringVar(value="100")
        self._entry(row, self.prop_h, 5).pack(side=tk.LEFT)
        
        # Блокировка
        row = self._row(sec)
        self.prop_locked = tk.BooleanVar(value=False)
        self._checkbox(row, "Заблокировать размер", self.prop_locked).pack(side=tk.LEFT)
        
        # Цвет заливки
        row = self._row(sec)
        self._label(row, "Заливка:").pack(side=tk.LEFT)
        self.prop_fill_color = tk.StringVar(value="")
        fill_entry = self._entry(row, self.prop_fill_color, 7)
        fill_entry.pack(side=tk.LEFT)
        self.fill_btn = tk.Button(row, text="◼", font=("Arial", 8), width=2,
                                  bg="#3a3a3a", fg="#888", relief=tk.FLAT,
                                  command=self._pick_fill_color, cursor="hand2")
        self.fill_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Цвет обводки
        row = self._row(sec)
        self._label(row, "Обводка:").pack(side=tk.LEFT)
        self.prop_stroke_color = tk.StringVar(value="#ffffff")
        stroke_entry = self._entry(row, self.prop_stroke_color, 7)
        stroke_entry.pack(side=tk.LEFT)
        self.stroke_btn = tk.Button(row, text="◼", font=("Arial", 8), width=2,
                                    bg="#ffffff", fg="#fff", relief=tk.FLAT,
                                    command=self._pick_stroke_color, cursor="hand2")
        self.stroke_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Толщина и прозрачность
        row = self._row(sec)
        self._label(row, "Толщина:").pack(side=tk.LEFT)
        self.prop_stroke_width = tk.StringVar(value="2")
        self._entry(row, self.prop_stroke_width, 3).pack(side=tk.LEFT)
        self._label(row, "Opacity:", 6).pack(side=tk.LEFT, padx=(8, 0))
        self.prop_opacity = tk.StringVar(value="100")
        self._entry(row, self.prop_opacity, 4).pack(side=tk.LEFT)
        self._label(row, "%").pack(side=tk.LEFT)
        
        # Скругление углов
        row = self._row(sec)
        self._label(row, "Скругление:").pack(side=tk.LEFT)
        self.prop_corner_radius = tk.StringVar(value="0")
        self._entry(row, self.prop_corner_radius, 4).pack(side=tk.LEFT)
        self._label(row, "px").pack(side=tk.LEFT)
        
        # Применить и расширенные настройки
        row = self._row(sec)
        self._button(row, "Применить", self._apply_props, 'primary').pack(side=tk.LEFT)
        self._button(row, "🔧 Расширенные...", self._show_extended, 'secondary').pack(side=tk.LEFT, padx=(8, 0))
        
        # === ФУНКЦИОНАЛЬНЫЕ АРТЕФАКТЫ ===
        sec = self._section(self.content, "◆ Функц. артефакты")
        
        # Описание
        tk.Label(sec, text="Панели с функционалом", font=("Arial", 8),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED).pack(anchor="w")
        
        # Кнопки артефактов
        func_grid = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        func_grid.pack(fill=tk.X, pady=(4, 0))
        
        # Список функциональных артефактов
        self.FUNC_ARTIFACTS = [
            ('file_browser', '📁', 'Файловый браузер'),
            ('code_editor', '💻', 'Редактор кода'),
            ('color_picker', '🎨', 'Палитра'),
            ('console', '▣', 'Консоль'),
        ]
        
        for i, (art_id, sym, name) in enumerate(self.FUNC_ARTIFACTS):
            btn = tk.Button(func_grid, text=sym, font=("Segoe UI", 12),
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                           activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                           relief=tk.FLAT, width=3, height=1, cursor="hand2",
                           command=lambda a=art_id: self._create_func_artifact(a))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            self._tooltip(btn, name)
        
        for c in range(4):
            func_grid.columnconfigure(c, weight=1)
        
        self.func_art_status = tk.Label(sec, text="", font=("Arial", 9),
                                       bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_ACCENT)
        self.func_art_status.pack(anchor="w", pady=(4, 0))
        
        # === Список артефактов на холсте ===
        sec = self._section(self.content, "Артефакты на холсте")
        
        self.artifacts_list = tk.Listbox(sec, height=4, font=("Consolas", 9),
                                        bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                        selectbackground=self.COLOR_ACCENT,
                                        selectforeground='#fff',
                                        highlightthickness=0, relief='flat')
        self.artifacts_list.pack(fill=tk.X, pady=2)
        self.artifacts_list.bind('<<ListboxSelect>>', self._on_artifact_list_select)
        
        # Кнопки управления артефактами
        art_toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        art_toolbar.pack(fill=tk.X)
        
        for sym, tip, cmd in [('⚙', 'Настройки', self._artifact_settings),
                              ('⧉', 'Дублировать', self._artifact_duplicate),
                              ('✕', 'Удалить', self._artifact_delete)]:
            b = self._icon_button(art_toolbar, sym, cmd)
            b.pack(side=tk.LEFT, padx=1)
            self._tooltip(b, tip)
        
        # === Настройки выбранного артефакта ===
        self.artifact_settings_frame = tk.Frame(self.content, bg=self.COLOR_BG)
        self.artifact_settings_frame.pack(fill=tk.X, pady=(8, 0))
        # Будет заполняться динамически при выборе артефакта
        
        # === ОБЫЧНЫЕ АРТЕФАКТЫ (шаблоны) ===
        art_sec = tk.Frame(self.content, bg=self.COLOR_BG)
        art_sec.pack(fill=tk.X, pady=(8, 0))
        
        tk.Label(art_sec, text="◇ Шаблоны", bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED,
                font=("Arial", 9)).pack(anchor="w", padx=4)
        
        # Строка шаблонов с прокруткой
        self.artifacts_scroll_container, self.artifacts_frame = self._create_scrollable_row(art_sec, 38)
        
        # Строка элементов шаблона
        elem_sec = tk.Frame(self.content, bg=self.COLOR_BG)
        elem_sec.pack(fill=tk.X, pady=(4, 0))
        
        self.artifact_info_lbl = tk.Label(elem_sec, text="○ Доп. элементы",
                                         bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED,
                                         font=("Arial", 8))
        self.artifact_info_lbl.pack(anchor="w", padx=4)
        
        # Строка доп. элементов с прокруткой
        self.artifact_elements_scroll_container, self.artifact_elements_frame = self._create_scrollable_row(elem_sec, 34)

    def _create_scrollable_row(self, parent, height=36):
        """
        Создаёт горизонтально прокручиваемую строку со стрелками.
        
        Returns:
            (container, inner_frame) - контейнер и внутренний фрейм для элементов
        """
        container = tk.Frame(parent, bg=self.COLOR_BG_SECONDARY)
        container.pack(fill=tk.X, padx=2, pady=2)
        
        # Левая стрелка
        left_btn = tk.Button(container, text="◀", font=("Arial", 8),
                            bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED,
                            activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                            relief=tk.FLAT, width=2, cursor="hand2")
        left_btn.pack(side=tk.LEFT, fill=tk.Y)
        
        # Canvas для прокрутки
        canvas = tk.Canvas(container, bg=self.COLOR_BG_SECONDARY,
                          height=height, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Правая стрелка
        right_btn = tk.Button(container, text="▶", font=("Arial", 8),
                             bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED,
                             activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                             relief=tk.FLAT, width=2, cursor="hand2")
        right_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Внутренний фрейм для элементов
        inner_frame = tk.Frame(canvas, bg=self.COLOR_BG_SECONDARY)
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        
        # Переменная для хранения смещения
        scroll_offset = [0]
        
        def update_scroll_region(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Обновляем видимость стрелок
            bbox = canvas.bbox("all")
            if bbox:
                content_width = bbox[2] - bbox[0]
                canvas_width = canvas.winfo_width()
                
                if content_width <= canvas_width:
                    # Контент помещается - скрываем стрелки
                    left_btn.config(state='disabled', fg=self.COLOR_BG_SECONDARY)
                    right_btn.config(state='disabled', fg=self.COLOR_BG_SECONDARY)
                else:
                    # Обновляем состояние стрелок
                    left_btn.config(state='normal' if scroll_offset[0] > 0 else 'disabled',
                                   fg=self.COLOR_TEXT_MUTED if scroll_offset[0] > 0 else self.COLOR_BG_SECONDARY)
                    max_offset = content_width - canvas_width
                    right_btn.config(state='normal' if scroll_offset[0] < max_offset else 'disabled',
                                    fg=self.COLOR_TEXT_MUTED if scroll_offset[0] < max_offset else self.COLOR_BG_SECONDARY)
        
        def scroll_left():
            scroll_offset[0] = max(0, scroll_offset[0] - 80)
            canvas.xview_moveto(scroll_offset[0] / max(1, canvas.bbox("all")[2]))
            update_scroll_region()
        
        def scroll_right():
            bbox = canvas.bbox("all")
            if bbox:
                max_offset = max(0, bbox[2] - canvas.winfo_width())
                scroll_offset[0] = min(max_offset, scroll_offset[0] + 80)
                canvas.xview_moveto(scroll_offset[0] / max(1, bbox[2]))
                update_scroll_region()
        
        left_btn.config(command=scroll_left)
        right_btn.config(command=scroll_right)
        
        # Привязываем обновление при изменении размера
        inner_frame.bind('<Configure>', update_scroll_region)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, height=e.height))
        
        # Прокрутка колесом мыши
        def on_mousewheel(event):
            if event.delta > 0 or event.num == 4:
                scroll_left()
            else:
                scroll_right()
        
        canvas.bind('<MouseWheel>', on_mousewheel)
        canvas.bind('<Button-4>', on_mousewheel)
        canvas.bind('<Button-5>', on_mousewheel)
        inner_frame.bind('<MouseWheel>', on_mousewheel)
        inner_frame.bind('<Button-4>', on_mousewheel)
        inner_frame.bind('<Button-5>', on_mousewheel)
        
        # Сохраняем ссылки для обновления
        container._scroll_canvas = canvas
        container._scroll_offset = scroll_offset
        container._update_scroll = update_scroll_region
        
        return container, inner_frame

    def _build_artifacts_section(self):
        """Создает секцию артефактов (заготовок)"""
        sec = self._section(self.content, "Артефакты")
        
        # Описание
        info_lbl = tk.Label(sec, text="Готовые компоненты с функционалом",
                           font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED)
        info_lbl.pack(fill=tk.X, padx=4, pady=2)
        
        # Кнопки артефактов
        artifacts_frame = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        artifacts_frame.pack(fill=tk.X, padx=4, pady=4)
        
        # Доступные артефакты
        artifacts_info = [
            ('file_browser', '📁', 'Браузер файлов', 'Панель навигации по файлам'),
            ('code_editor', '</>', 'Редактор кода', 'Редактор с подсветкой синтаксиса')
        ]
        
        for artifact_id, icon, name, description in artifacts_info:
            btn = tk.Button(
                artifacts_frame,
                text=f"{icon}\n{name}", font=("Arial", 9),
                bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                relief=tk.FLAT, cursor="hand2", width=12, height=3,
                command=lambda aid=artifact_id: self._create_artifact(aid)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self._tooltip(btn, f"{name}\n{description}\n\nКлик: создать артефакт")
        
        # Статус артефактов
        self.artifact_status_lbl = tk.Label(sec, text="Готово к размещению",
                                           font=("Arial", 8), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED)
        self.artifact_status_lbl.pack(fill=tk.X, padx=4, pady=2)

    def set_artifact_manager_integrated(self, manager):
        """Устанавливает интегрированный менеджер артефактов"""
        self.artifact_manager_integrated = manager

    

    def _create_artifact(self, artifact_id):
        """Начать создание артефакта"""
        if not self.artifact_manager_integrated:
            self.status_lbl.config(text="✗ Менеджер артефактов недоступен")
            return
        
        # Получаем информацию об артефакте
        available = self.artifact_manager_integrated.get_available_artifacts()
        if artifact_id not in available:
            self.status_lbl.config(text=f"✗ Неизвестный артефакт: {artifact_id}")
            return
        
        artifact_info = available[artifact_id]
        
        # Начинаем создание через обычный элемент-контейнер
        min_size = artifact_info['min_size']
        
        # Запоминаем тип артефакта для применения после создания элемента
        self._pending_artifact_type = artifact_id
        
        # Создаём панель как контейнер для артефакта
        if self.element_manager:
            self.element_manager.start_creation('panel')
            
            name = artifact_info['name']
            self.status_lbl.config(text=f"⏵ Создайте область для {name} (мин. {min_size['width']}×{min_size['height']})")
            self.artifact_status_lbl.config(text=f"Создание области для {name}...", fg=self.COLOR_ACCENT)
        else:
            self.status_lbl.config(text="✗ Менеджер элементов недоступен")

    def _create(self, etype):
        """Начать создание элемента"""
        if not self.element_manager:
            return
        
        name = next((n for t, s, n in self.ELEMENTS if t == etype), etype)
        
        
        self.status_lbl.config(text=f"⏵ {name}")
        
        for t, btn in self.btns.items():
            btn.config(bg=self.COLOR_ACCENT if t == etype else self.COLOR_BG,
                      fg='#fff' if t == etype else self.COLOR_TEXT)
        
        self.element_manager.start_creation(etype)

    def _on_tree_click(self, e=None):
        """Клик по списку"""
        if self._updating or not self.element_manager:
            return
        self._updating = True
        try:
            sel = self.tree.selection()
            if sel:
                for elem in self.element_manager.get_all_elements():
                    if elem.id == sel[0]:
                        self.element_manager.select_element(elem)
                        break
        finally:
            self._updating = False

    def _on_selection(self, elem):
        """Callback выбора элемента"""
        if self._updating:
            return
        self._updating = True
        
        try:
            self._refresh()
            self.status_lbl.config(text="")
            
            for btn in self.btns.values():
                btn.config(bg=self.COLOR_BG, fg=self.COLOR_TEXT)
            
            if elem:
                sym = getattr(elem, 'ELEMENT_SYMBOL', '?')
                etype = getattr(elem, 'ELEMENT_TYPE', '?')
                self.prop_type.config(text=f"{sym} {etype}")
                self.prop_x.set(str(int(elem.x)))
                self.prop_y.set(str(int(elem.y)))
                self.prop_w.set(str(int(elem.width)))
                self.prop_h.set(str(int(elem.height)))
                self.prop_locked.set(getattr(elem, 'size_locked', False))
                
                # Загружаем свойства элемента
                props = getattr(elem, 'properties', {})
                fill = props.get('fill_color', '')
                stroke = props.get('stroke_color', '#ffffff')
                stroke_w = props.get('stroke_width', 2)
                opacity = props.get('opacity', 100)
                radius = props.get('corner_radius', 0)
                
                self.prop_fill_color.set(fill if fill else '')
                self.prop_stroke_color.set(stroke)
                self.prop_stroke_width.set(str(stroke_w))
                self.prop_opacity.set(str(opacity))
                self.prop_corner_radius.set(str(radius))
                
                # Обновляем цвета кнопок
                self._update_color_buttons(fill, stroke)
                
            
            # Если был создан элемент для размещения артефакта
            elif self._pending_artifact_type and self.artifact_manager_integrated:
                self._place_artifact_in_element(elem)
                
                try:
                    self.tree.selection_set(elem.id)
                    self.tree.see(elem.id)
                except tk.TclError:
                    pass  # Item not found in tree
            else:
                self.prop_type.config(text="—")
                self.prop_x.set("0")
                self.prop_y.set("0")
                self.prop_w.set("100")
                self.prop_h.set("100")
                self.prop_locked.set(False)
                self.prop_fill_color.set("")
                self.prop_stroke_color.set("#ffffff")
                self.prop_stroke_width.set("2")
                self.prop_opacity.set("100")
                self.prop_corner_radius.set("0")
                self._update_color_buttons("", "#ffffff")
        finally:
            self._updating = False


    def _place_artifact_in_element(self, element):
        """Размещает артефакт внутри созданного элемента"""
        if not self._pending_artifact_type or not self.artifact_manager_integrated:
            return
        
        try:
            # Создаем артефакт в позиции элемента
            artifact = self.artifact_manager_integrated.create_artifact_at(
                element.x, element.y, element.width, element.height
            )
            
            if artifact:
                # Удаляем элемент-контейнер (он больше не нужен)
                if self.element_manager:
                    self.element_manager.delete_element(element)
                
                artifact_info = self.artifact_manager_integrated.get_available_artifacts()
                name = artifact_info.get(self._pending_artifact_type, {}).get('name', 'Артефакт')
                
                self.status_lbl.config(text=f"✓ {name} размещён")
                self.artifact_status_lbl.config(text="Готово к размещению", fg=self.COLOR_TEXT_MUTED)
            else:
                self.status_lbl.config(text="✗ Ошибка размещения артефакта")
        
        except Exception as e:
            self.status_lbl.config(text=f"✗ Ошибка: {str(e)}")
        finally:
            self._pending_artifact_type = None

    def _update_color_buttons(self, fill, stroke):
        """Обновляет цвета кнопок выбора цвета"""
        try:
            if fill and fill != '':
                self.fill_btn.config(bg=fill)
            else:
                self.fill_btn.config(bg="#3a3a3a")
            
            if stroke:
                self.stroke_btn.config(bg=stroke)
        except tk.TclError:
            pass
    
    def _pick_fill_color(self):
        """Выбор цвета заливки"""
        from tkinter import colorchooser
        current = self.prop_fill_color.get()
        color = colorchooser.askcolor(color=current if current else "#ffffff",
                                      title="Цвет заливки")
        if color[1]:
            self.prop_fill_color.set(color[1])
            self.fill_btn.config(bg=color[1])
    
    def _pick_stroke_color(self):
        """Выбор цвета обводки"""
        from tkinter import colorchooser
        current = self.prop_stroke_color.get()
        color = colorchooser.askcolor(color=current if current else "#ffffff",
                                      title="Цвет обводки")
        if color[1]:
            self.prop_stroke_color.set(color[1])
            self.stroke_btn.config(bg=color[1])

    def _apply_props(self):
        """Применить свойства"""
        if not self.element_manager or not self.element_manager.selected_element:
            return
        
        elem = self.element_manager.selected_element
        try:
            # Позиция и размер
            elem.x = int(self.prop_x.get())
            elem.y = int(self.prop_y.get())
            elem.width = int(self.prop_w.get())
            elem.height = int(self.prop_h.get())
            elem.size_locked = self.prop_locked.get()
            
            # Цвета и стили
            fill = self.prop_fill_color.get().strip()
            stroke = self.prop_stroke_color.get().strip()
            stroke_w = int(self.prop_stroke_width.get())
            opacity = int(self.prop_opacity.get())
            radius = int(self.prop_corner_radius.get())
            
            # Применяем к свойствам элемента
            if hasattr(elem, 'properties'):
                elem.properties['fill_color'] = fill
                elem.properties['stroke_color'] = stroke
                elem.properties['stroke_width'] = max(0, stroke_w)
                elem.properties['opacity'] = max(0, min(100, opacity))
                elem.properties['corner_radius'] = max(0, radius)
            
            elem.update()
            self._refresh()
            
            # Обновляем selection tool если есть
            if hasattr(self, '_app') and self._app and hasattr(self._app, 'selection_tool'):
                self._app.selection_tool.update()
                
        except ValueError as e:
            print(f"[TabElements] Ошибка применения свойств: {e}")
    
    def _show_extended(self):
        """Показать расширенные настройки элемента"""
        if not self.element_manager or not self.element_manager.selected_element:
            return
        
        elem = self.element_manager.selected_element
        
        try:
            from modules.dialogs.element_extended_dialog import show_element_extended_dialog
            
            # Получаем mechanism_manager через element_manager если есть
            mechanism_manager = None
            if hasattr(self.element_manager, '_mechanism_manager'):
                mechanism_manager = self.element_manager._mechanism_manager
            
            result = show_element_extended_dialog(
                self.frame.winfo_toplevel(),
                elem,
                self.element_manager,
                mechanism_manager
            )
            
            if result:
                self._refresh()
        except ImportError as e:
            print(f"[TabElements] Ошибка импорта диалога: {e}")

    def _refresh(self):
        """Обновить список"""
        if not self.tree or not self.element_manager:
            return
        
        sel = self.tree.selection()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for elem in self.element_manager.get_all_elements():
            sym = getattr(elem, 'ELEMENT_SYMBOL', '?')
            name = elem.id[:12]
            size = f"{int(elem.width)}×{int(elem.height)}"
            self.tree.insert('', 'end', iid=elem.id, values=(sym, name, size))
        
        if sel:
            try:
                self.tree.selection_set(sel)
            except tk.TclError:
                pass  # Item not found

    def _up(self):
        if self.element_manager and self.element_manager.selected_element:
            self.element_manager.bring_to_front(self.element_manager.selected_element)
            self._refresh()

    def _down(self):
        if self.element_manager and self.element_manager.selected_element:
            self.element_manager.send_to_back(self.element_manager.selected_element)
            self._refresh()

    def _copy(self):
        if self.element_manager and self.element_manager.selected_element:
            elem = self.element_manager.selected_element
            self.element_manager.start_creation(elem.ELEMENT_TYPE)

    def _delete(self):
        if self.element_manager:
            self.element_manager.delete_selected()
            self._refresh()
            self._on_selection(None)

    def on_activate(self):
        self._refresh()
        self._refresh_artifacts()
    
    # === Методы артефактов ===
    
    def _refresh_artifacts(self):
        """Обновляет строку артефактов"""
        if not self.artifacts_frame:
            return
        for w in self.artifacts_frame.winfo_children():
            w.destroy()
        self.artifact_btns.clear()
        
        if not self.artifact_manager:
            # Обновляем прокрутку
            if hasattr(self, 'artifacts_scroll_container') and hasattr(self.artifacts_scroll_container, '_update_scroll'):
                self.frame.after(50, self.artifacts_scroll_container._update_scroll)
            return
        
        # Встроенные артефакты
        BUILTIN = [
            ('directory_browser', '📁', 'Папки'),
            ('card', '▢', 'Карточка'),
            ('menu', '☰', 'Меню'),
        ]
        
        for atype, icon, name in BUILTIN:
            btn = tk.Button(self.artifacts_frame,
                           text=f"{icon} {name}",
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                           font=("Arial", 9), relief=tk.FLAT, padx=6, pady=4,
                           activebackground=self.COLOR_ACCENT, cursor="hand2",
                           command=lambda t=atype: self._place_artifact(t))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            btn.bind('<Button-3>', lambda e, t=atype: self._artifact_menu(e, t))
            self._tooltip(btn, f"Разместить: {name}")
            self.artifact_btns[atype] = btn
        
        # Пользовательские артефакты
        if self.artifact_manager:
            for artifact in self.artifact_manager.get_all_artifacts():
                btn = tk.Button(self.artifacts_frame,
                               text=f"{artifact.icon} {artifact.name[:8]}",
                               bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                               font=("Arial", 9), relief=tk.FLAT, padx=4, pady=4,
                               activebackground=self.COLOR_ACCENT, cursor="hand2",
                               command=lambda a=artifact: self._select_custom_artifact(a))
                btn.pack(side=tk.LEFT, padx=1, pady=2)
                btn.bind('<Button-3>', lambda e, a=artifact: self._custom_artifact_menu(e, a))
                self._tooltip(btn, artifact.description or artifact.name)
                self.artifact_btns[artifact.id] = btn
        
        # Обновляем прокрутку
        if hasattr(self, 'artifacts_scroll_container') and hasattr(self.artifacts_scroll_container, '_update_scroll'):
            self.frame.after(50, self.artifacts_scroll_container._update_scroll)
    
    def _place_artifact(self, artifact_type):
        """Размещает встроенный артефакт"""
        if not self.element_manager:
            return
        
        # Подсветка
        for aid, btn in self.artifact_btns.items():
            btn.config(bg=self.COLOR_ACCENT if aid == artifact_type else self.COLOR_BG,
                      fg='#fff' if aid == artifact_type else self.COLOR_TEXT)
        
        self.selected_artifact = artifact_type
        self.element_manager.start_creation('artifact', artifact_type=artifact_type)
        
        names = {'directory_browser': 'Папки', 'card': 'Карточка', 'menu': 'Меню'}
        self.status_lbl.config(text=f"⏵ {names.get(artifact_type, 'Артефакт')}")
        
        # Показываем доп. элементы
        self._show_artifact_extras(artifact_type)
    
    def _show_artifact_extras(self, artifact_type):
        """Показывает дополнительные элементы артефакта"""
        for w in self.artifact_elements_frame.winfo_children():
            w.destroy()
        
        # Дополнительные элементы для каждого типа
        EXTRAS = {
            'directory_browser': [
                ('header', '▬', 'Заголовок'),
                ('search', '⌕', 'Поиск'),
                ('toolbar', '▤', 'Тулбар'),
                ('footer', '▬', 'Подвал'),
            ],
            'card': [
                ('image', '▣', 'Картинка'),
                ('title', 'T', 'Заголовок'),
                ('badge', '●', 'Бейдж'),
                ('action', '⬚', 'Кнопка'),
            ],
            'menu': [
                ('item', '●', 'Пункт'),
                ('divider', '—', 'Разделитель'),
                ('submenu', '▶', 'Подменю'),
            ],
        }
        
        extras = EXTRAS.get(artifact_type, [])
        
        if extras:
            self.artifact_info_lbl.config(text=f"● Доп. элементы", fg=self.COLOR_ACCENT)
            
            for etype, icon, name in extras:
                btn = tk.Button(self.artifact_elements_frame,
                               text=f"{icon} {name}",
                               bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                               font=("Arial", 8), relief=tk.FLAT, padx=4, pady=2,
                               activebackground=self.COLOR_ACCENT, cursor="hand2",
                               command=lambda t=etype: self._place_extra(t))
                btn.pack(side=tk.LEFT, padx=1, pady=2)
                self._tooltip(btn, f"Добавить: {name}")
        else:
            self.artifact_info_lbl.config(text="○ Доп. элементы", fg=self.COLOR_TEXT_MUTED)
        
        # Обновляем прокрутку
        if hasattr(self, 'artifact_elements_scroll_container') and hasattr(self.artifact_elements_scroll_container, '_update_scroll'):
            self.frame.after(50, self.artifact_elements_scroll_container._update_scroll)
    
    def _place_extra(self, extra_type):
        """Размещает дополнительный элемент артефакта"""
        if not self.element_manager:
            return
        
        # Мапинг на реальные элементы
        type_map = {
            'header': 'panel', 'search': 'panel', 'toolbar': 'panel',
            'footer': 'panel', 'image': 'panel', 'title': 'text',
            'badge': 'panel', 'action': 'button', 'item': 'button',
            'divider': 'panel', 'submenu': 'panel'
        }
        
        etype = type_map.get(extra_type, 'panel')
        self.element_manager.start_creation(etype)
        self.status_lbl.config(text=f"⏵ {extra_type}")
    
    def _artifact_menu(self, event, artifact_type):
        """Контекстное меню встроенного артефакта"""
        menu = tk.Menu(self, tearoff=0, bg=self.COLOR_BG_SECONDARY, 
                       fg=self.COLOR_TEXT, font=("Arial", 9))
        
        menu.add_command(label="◆ Разместить", 
                        command=lambda: self._place_artifact(artifact_type))
        menu.add_separator()
        menu.add_command(label="⚙ Настройки стиля", 
                        command=lambda: self._edit_builtin_style(artifact_type))
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def _edit_builtin_style(self, artifact_type):
        """Редактирует стиль встроенного артефакта"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Стиль: {artifact_type}")
        dialog.geometry("300x200")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Настройки стиля артефакта",
                bg=self.COLOR_BG, fg=self.COLOR_ACCENT,
                font=("Arial", 10, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="(Будут применены при размещении)",
                bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED,
                font=("Arial", 9)).pack(pady=5)
        
        tk.Button(dialog, text="OK", command=dialog.destroy,
                 bg=self.COLOR_ACCENT, fg='#fff', relief=tk.FLAT).pack(pady=20)
    
    def _select_custom_artifact(self, artifact):
        """Выбирает пользовательский артефакт"""
        if self.artifact_manager:
            self.artifact_manager.select_artifact(artifact)
    
    def _on_artifact_selected(self, artifact):
        """Колбэк выбора артефакта"""
        self.selected_artifact = artifact
        if artifact:
            self._show_custom_artifact_elements(artifact)
        else:
            self._clear_artifact_extras()
    
    def _show_custom_artifact_elements(self, artifact):
        """Показывает элементы пользовательского артефакта"""
        for w in self.artifact_elements_frame.winfo_children():
            w.destroy()
        
        if artifact.elements:
            self.artifact_info_lbl.config(text=f"● {artifact.name}", fg=self.COLOR_ACCENT)
            
            for elem in artifact.elements:
                btn = tk.Button(self.artifact_elements_frame,
                               text=f"{elem.get('icon', '○')} {elem.get('name', '')[:8]}",
                               bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                               font=("Arial", 8), relief=tk.FLAT, padx=3, pady=2,
                               activebackground=self.COLOR_ACCENT, cursor="hand2",
                               command=lambda e=elem: self._place_custom_element(e))
                btn.pack(side=tk.LEFT, padx=1, pady=2)
        else:
            self.artifact_info_lbl.config(text="○ Доп. элементы", fg=self.COLOR_TEXT_MUTED)
        
        # Обновляем прокрутку
        if hasattr(self, 'artifact_elements_scroll_container') and hasattr(self.artifact_elements_scroll_container, '_update_scroll'):
            self.frame.after(50, self.artifact_elements_scroll_container._update_scroll)
    
    def _place_custom_element(self, elem_data):
        """Размещает элемент пользовательского артефакта"""
        if not self.element_manager:
            return
        self.element_manager.start_creation('panel')
        self.status_lbl.config(text=f"⏵ {elem_data.get('name', 'Элемент')}")
    
    
    
    def _clear_artifact_extras(self):
        """Очищает строку доп. элементов"""
        for w in self.artifact_elements_frame.winfo_children():
            w.destroy()
        self.artifact_info_lbl.config(text="○ Доп. элементы", fg=self.COLOR_TEXT_MUTED)
        
        # Обновляем прокрутку
        if hasattr(self, 'artifact_elements_scroll_container') and hasattr(self.artifact_elements_scroll_container, '_update_scroll'):
            self.frame.after(50, self.artifact_elements_scroll_container._update_scroll)
    
    def _custom_artifact_menu(self, event, artifact):
        """Контекстное меню пользовательского артефакта"""
        menu = tk.Menu(self, tearoff=0, bg=self.COLOR_BG_SECONDARY, 
                       fg=self.COLOR_TEXT, font=("Arial", 9))
        
        menu.add_command(label="◆ Разместить", 
                        command=lambda: self._place_custom_artifact(artifact))
        menu.add_separator()
        menu.add_command(label="✎ Переименовать", 
                        command=lambda: self._rename_artifact(artifact))
        menu.add_command(label="⚙ Стиль", 
                        command=lambda: self._edit_artifact_style(artifact))
        menu.add_separator()
        menu.add_command(label="✕ Удалить", 
                        command=lambda: self._delete_artifact(artifact))
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def _place_custom_artifact(self, artifact):
        """Размещает пользовательский артефакт"""
        if not self.element_manager:
            return
        self.element_manager.start_creation('panel')
        self.status_lbl.config(text=f"⏵ {artifact.name}")
    
    def _rename_artifact(self, artifact):
        """Переименование артефакта"""
        dialog = tk.Toplevel(self)
        dialog.title("Переименовать")
        dialog.geometry("280x90")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Имя:", bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(pady=5)
        entry = tk.Entry(dialog, bg=self.COLOR_BG_SECONDARY, fg=self.COLOR_TEXT,
                        insertbackground=self.COLOR_TEXT, width=30)
        entry.pack(padx=10)
        entry.insert(0, artifact.name)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save():
            artifact.name = entry.get()
            if self.artifact_manager:
                self.artifact_manager._save_artifact(artifact)
            self._refresh_artifacts()
            dialog.destroy()
        
        tk.Button(dialog, text="OK", command=save, bg=self.COLOR_ACCENT, 
                 fg='#fff', relief=tk.FLAT).pack(pady=8)
        entry.bind('<Return>', lambda e: save())
    
    def _edit_artifact_style(self, artifact):
        """Редактирование стиля артефакта"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Стиль: {artifact.name}")
        dialog.geometry("300x250")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()
        
        entries = {}
        colors = [('bg_color', 'Фон'), ('text_color', 'Текст'), 
                  ('accent_color', 'Акцент'), ('border_color', 'Границы')]
        
        for key, label in colors:
            row = tk.Frame(dialog, bg=self.COLOR_BG)
            row.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(row, text=label, width=10, anchor='w',
                    bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
            entry = tk.Entry(row, width=12, bg=self.COLOR_BG_SECONDARY, 
                            fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT)
            entry.pack(side=tk.LEFT, padx=5)
            entry.insert(0, artifact.style.get(key, '#000000'))
            entries[key] = entry
        
        def save():
            for key, entry in entries.items():
                artifact.style[key] = entry.get()
            if self.artifact_manager:
                self.artifact_manager._save_artifact(artifact)
            dialog.destroy()
        
        tk.Button(dialog, text="Сохранить", command=save, bg=self.COLOR_ACCENT, 
                 fg='#fff', relief=tk.FLAT).pack(pady=15)
    
    def _delete_artifact(self, artifact):
        """Удаляет артефакт"""
        from tkinter import messagebox
        if messagebox.askyesno("Удалить", f"Удалить '{artifact.name}'?"):
            if self.artifact_manager:
                self.artifact_manager.remove_artifact(artifact)
                self._refresh_artifacts()
                self._clear_artifact_extras()
    
    # === ФУНКЦИОНАЛЬНЫЕ АРТЕФАКТЫ ===
    
    def _create_func_artifact(self, artifact_id):
        """Начинает режим создания функционального артефакта (рисование области)"""
        try:
            from modules.artifacts import ArtifactRegistry
        except ImportError:
            self.func_art_status.config(text="❌ Модуль не найден")
            return
        
        # Проверяем доступность
        available = ArtifactRegistry.get_available()
        if artifact_id not in available:
            self.func_art_status.config(text=f"⚠ {artifact_id} не реализован")
            return
        
        name = next((n for a, s, n in self.FUNC_ARTIFACTS if a == artifact_id), artifact_id)
        self.func_art_status.config(text=f"⏵ Нарисуйте область для: {name}")
        
        # Сохраняем тип артефакта для создания
        self._pending_artifact_id = artifact_id
        
        # Запускаем режим рисования области
        if self.element_manager and hasattr(self.element_manager, 'canvas'):
            canvas = self.element_manager.canvas
            
            # Привязываем события для рисования
            canvas.bind('<Button-1>', self._on_artifact_draw_start)
            canvas.bind('<B1-Motion>', self._on_artifact_draw_drag)
            canvas.bind('<ButtonRelease-1>', self._on_artifact_draw_end)
            
            # Прямоугольник превью
            self._artifact_preview_rect = None
            self._artifact_draw_start = None
            
            # Меняем курсор
            canvas.config(cursor='crosshair')
        return
    
    def _on_artifact_draw_start(self, event):
        """Начало рисования области артефакта"""
        self._artifact_draw_start = (event.x, event.y)
        if self.element_manager and hasattr(self.element_manager, 'canvas'):
            canvas = self.element_manager.canvas
            self._artifact_preview_rect = canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline='#2f81f7', width=2, dash=(6, 4),
                fill='', tags='artifact_preview'
            )
    
    def _on_artifact_draw_drag(self, event):
        """Перетаскивание при рисовании области"""
        if self._artifact_draw_start and self._artifact_preview_rect:
            x1, y1 = self._artifact_draw_start
            if self.element_manager and hasattr(self.element_manager, 'canvas'):
                canvas = self.element_manager.canvas
                canvas.coords(self._artifact_preview_rect, x1, y1, event.x, event.y)
    
    def _on_artifact_draw_end(self, event):
        """Завершение рисования - создаём артефакт"""
        if not self._artifact_draw_start or not hasattr(self, '_pending_artifact_id'):
            return
        
        x1, y1 = self._artifact_draw_start
        x2, y2 = event.x, event.y
        
        # Нормализуем координаты
        left = min(x1, x2)
        top = min(y1, y2)
        width = max(abs(x2 - x1), 150)  # Минимум 150
        height = max(abs(y2 - y1), 150)
        
        # Удаляем превью
        if self.element_manager and hasattr(self.element_manager, 'canvas'):
            canvas = self.element_manager.canvas
            if self._artifact_preview_rect:
                canvas.delete(self._artifact_preview_rect)
            
            # Убираем привязки артефактов
            canvas.unbind('<Button-1>')
            canvas.unbind('<B1-Motion>')
            canvas.unbind('<ButtonRelease-1>')
            canvas.config(cursor='')
            
            # Восстанавливаем обработчики приложения
            if hasattr(self, '_app') and self._app and hasattr(self._app, 'event_handlers'):
                self._app.event_handlers.bind_canvas_events(canvas, self._app.root)
        
        # Создаём артефакт
        self._do_create_func_artifact(self._pending_artifact_id, left, top, width, height)
        
        # Очищаем
        self._artifact_draw_start = None
        self._artifact_preview_rect = None
        self._pending_artifact_id = None
    
    def _do_create_func_artifact(self, artifact_id, x, y, width, height):
        """Непосредственно создаёт функциональный артефакт"""
        try:
            from modules.artifacts import ArtifactRegistry
        except ImportError:
            return
        
        name = next((n for a, s, n in self.FUNC_ARTIFACTS if a == artifact_id), artifact_id)
        
        # Получаем canvas и размещаем артефакт
        if self.element_manager and self.element_manager.canvas:
            canvas = self.element_manager.canvas
            
            # Создаём артефакт с заданными координатами и размером
            artifact = ArtifactRegistry.create(
                artifact_id, canvas, 
                int(x), int(y),
                width=int(width), height=int(height)
            )
            
            if artifact:
                artifact.set_select_callback(self._on_func_artifact_select)
                self._refresh_artifacts_list()
                self.func_art_status.config(text=f"✓ {name} создан ({int(width)}×{int(height)})")
            else:
                self.func_art_status.config(text=f"❌ Ошибка создания")
        else:
            self.func_art_status.config(text="⚠ Canvas недоступен")
    
    def _on_func_artifact_select(self, artifact):
        """Колбэк выбора функционального артефакта"""
        self._show_func_artifact_settings(artifact)
        self._refresh_artifacts_list()
    
    def _show_func_artifact_settings(self, artifact):
        """Показывает настройки функционального артефакта в боковой панели"""
        # Очищаем предыдущие настройки
        for w in self.artifact_settings_frame.winfo_children():
            w.destroy()
        
        if not artifact:
            return
        
        # Заголовок
        header = tk.Frame(self.artifact_settings_frame, bg=self.COLOR_BG_OVERLAY)
        header.pack(fill=tk.X, padx=4, pady=4)
        
        tk.Label(header, text=f"{artifact.ARTIFACT_ICON} {artifact.ARTIFACT_NAME}",
                font=("Arial", 10, "bold"), bg=self.COLOR_BG_OVERLAY,
                fg=self.COLOR_ACCENT).pack(anchor='w')
        
        # Поля настроек
        fields = artifact.get_settings_fields()
        
        settings_vars = {}
        for field in fields:
            row = tk.Frame(self.artifact_settings_frame, bg=self.COLOR_BG)
            row.pack(fill=tk.X, padx=4, pady=2)
            
            tk.Label(row, text=field['label'], font=("Arial", 9),
                    bg=self.COLOR_BG, fg=self.COLOR_TEXT, width=12, anchor='w').pack(side=tk.LEFT)
            
            if field['type'] == 'checkbox':
                var = tk.BooleanVar(value=field['value'])
                cb = tk.Checkbutton(row, variable=var, bg=self.COLOR_BG,
                                   activebackground=self.COLOR_BG,
                                   selectcolor=self.COLOR_BG_SECONDARY)
                cb.pack(side=tk.LEFT)
                settings_vars[field['id']] = var
                
            elif field['type'] == 'path':
                var = tk.StringVar(value=field['value'])
                entry = tk.Entry(row, textvariable=var, width=18,
                               font=("Consolas", 9), bg=self.COLOR_BG_SECONDARY,
                               fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                settings_vars[field['id']] = var
                
                # Кнопка обзора
                from tkinter import filedialog
                browse_btn = tk.Button(row, text="...", font=("Arial", 8),
                                      bg=self.COLOR_BG_SECONDARY, fg=self.COLOR_TEXT,
                                      relief='flat', padx=4,
                                      command=lambda v=var: v.set(
                                          filedialog.askdirectory() or v.get()))
                browse_btn.pack(side=tk.RIGHT, padx=(2, 0))
            else:
                var = tk.StringVar(value=str(field['value']))
                entry = tk.Entry(row, textvariable=var, width=15,
                               font=("Arial", 9), bg=self.COLOR_BG_SECONDARY,
                               fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT)
                entry.pack(side=tk.LEFT)
                settings_vars[field['id']] = var
        
        # Кнопка применить
        btn_row = tk.Frame(self.artifact_settings_frame, bg=self.COLOR_BG)
        btn_row.pack(fill=tk.X, padx=4, pady=(8, 4))
        
        def apply_settings():
            settings = {}
            for field_id, var in settings_vars.items():
                settings[field_id] = var.get()
            artifact.apply_settings(settings)
            self.func_art_status.config(text="✓ Настройки применены")
        
        tk.Button(btn_row, text="Применить", font=("Arial", 9),
                 bg=self.COLOR_ACCENT, fg='#fff', relief='flat',
                 padx=12, command=apply_settings).pack(side=tk.LEFT)
    
    def _refresh_artifacts_list(self):
        """Обновляет список артефактов на холсте"""
        if not hasattr(self, 'artifacts_list'):
            return
        
        self.artifacts_list.delete(0, tk.END)
        
        try:
            from modules.artifacts import ArtifactRegistry
            for artifact in ArtifactRegistry.get_instances():
                name = f"{artifact.ARTIFACT_ICON} {artifact.ARTIFACT_NAME}"
                self.artifacts_list.insert(tk.END, name)
        except ImportError:
            pass
    
    def _on_artifact_list_select(self, event):
        """Выбор артефакта из списка"""
        sel = self.artifacts_list.curselection()
        if not sel:
            return
        
        try:
            from modules.artifacts import ArtifactRegistry
            instances = ArtifactRegistry.get_instances()
            if sel[0] < len(instances):
                artifact = instances[sel[0]]
                artifact.select()
        except ImportError:
            pass
    
    def _artifact_settings(self):
        """Настройки выбранного артефакта"""
        try:
            from modules.artifacts import ArtifactRegistry
            instances = ArtifactRegistry.get_instances()
            for artifact in instances:
                if artifact._selected:
                    artifact._show_settings()
                    return
        except ImportError:
            pass
    
    def _artifact_duplicate(self):
        """Дублирует выбранный артефакт"""
        try:
            from modules.artifacts import ArtifactRegistry
            instances = ArtifactRegistry.get_instances()
            for artifact in instances:
                if artifact._selected:
                    # Создаём копию
                    new_artifact = ArtifactRegistry.create(
                        artifact.ARTIFACT_ID,
                        artifact.parent_canvas,
                        artifact.x + 30,
                        artifact.y + 30,
                        width=artifact.width,
                        height=artifact.height,
                        config=artifact.config.copy()
                    )
                    if new_artifact:
                        new_artifact.set_select_callback(self._on_func_artifact_select)
                        self._refresh_artifacts_list()
                    return
        except ImportError:
            pass
    
    def _artifact_delete(self):
        """Удаляет выбранный функциональный артефакт"""
        try:
            from modules.artifacts import ArtifactRegistry
            instances = ArtifactRegistry.get_instances()
            for artifact in instances:
                if artifact._selected:
                    ArtifactRegistry.remove(artifact)
                    self._refresh_artifacts_list()
                    # Очищаем настройки
                    for w in self.artifact_settings_frame.winfo_children():
                        w.destroy()
                    return
        except ImportError:
            pass
