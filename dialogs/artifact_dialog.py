#!/usr/bin/env python3
"""
Диалоги для работы с артефактами/заготовками
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SaveArtifactDialog:
    """Диалог сохранения артефакта"""
    
    ICONS = ['📦', '🔘', '🔲', '📋', '🔧', '⚙️', '🎨', '💡', '⭐', '🔔', '📱', '💻']
    
    CATEGORIES = [
        "Пользовательские",
        "Кнопки",
        "Панели",
        "Формы",
        "Навигация",
        "Карточки",
        "Меню",
        "Модальные окна",
        "Анимации",
    ]

    def __init__(self, parent, element_count=0, mechanism_count=0):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Сохранить как заготовку")
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.configure(bg="#2a2a2a")
        
        self._build_ui(element_count, mechanism_count)
        self.dialog.wait_window()

    def _build_ui(self, element_count, mechanism_count):
        # Заголовок
        header = tk.Frame(self.dialog, bg="#2a2a2a")
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            header,
            text="📦 Сохранить как заготовку",
            font=("Arial", 14, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        ).pack(anchor="w")
        
        # Информация
        info_text = f"Элементов: {element_count} | Механизмов: {mechanism_count}"
        tk.Label(
            header,
            text=info_text,
            font=("Arial", 9),
            bg="#2a2a2a",
            fg="#888888"
        ).pack(anchor="w")
        
        # Основная форма
        form = tk.Frame(self.dialog, bg="#2a2a2a")
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Название
        tk.Label(
            form,
            text="Название:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(anchor="w", pady=(0, 5))
        
        self.name_var = tk.StringVar(value="Новая заготовка")
        name_entry = tk.Entry(
            form,
            textvariable=self.name_var,
            font=("Arial", 11),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT
        )
        name_entry.pack(fill=tk.X, ipady=6)
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Иконка
        tk.Label(
            form,
            text="Иконка:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(anchor="w", pady=(15, 5))
        
        icons_frame = tk.Frame(form, bg="#2a2a2a")
        icons_frame.pack(fill=tk.X)
        
        self.icon_var = tk.StringVar(value="📦")
        for icon in self.ICONS:
            rb = tk.Radiobutton(
                icons_frame,
                text=icon,
                variable=self.icon_var,
                value=icon,
                font=("Arial", 14),
                bg="#2a2a2a",
                fg="#ffffff",
                selectcolor="#3a3a3a",
                activebackground="#2a2a2a",
                indicatoron=False,
                padx=8,
                pady=4
            )
            rb.pack(side=tk.LEFT, padx=2)
        
        # Категория
        tk.Label(
            form,
            text="Категория:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(anchor="w", pady=(15, 5))
        
        self.category_var = tk.StringVar(value="Пользовательские")
        category_combo = ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=self.CATEGORIES,
            state="readonly",
            font=("Arial", 10)
        )
        category_combo.pack(fill=tk.X)
        
        # Теги
        tk.Label(
            form,
            text="Теги (через запятую):",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(anchor="w", pady=(15, 5))
        
        self.tags_var = tk.StringVar()
        tags_entry = tk.Entry(
            form,
            textvariable=self.tags_var,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT
        )
        tags_entry.pack(fill=tk.X, ipady=4)
        
        # Описание
        tk.Label(
            form,
            text="Описание:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#cccccc"
        ).pack(anchor="w", pady=(15, 5))
        
        self.desc_text = tk.Text(
            form,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            height=4,
            wrap=tk.WORD
        )
        self.desc_text.pack(fill=tk.X)
        
        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(
            btn_frame,
            text="Сохранить",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            command=self._on_save
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=10)
        
        # Горячие клавиши
        self.dialog.bind('<Return>', lambda e: self._on_save())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())

    def _on_save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Предупреждение", "Введите название заготовки")
            return
        
        # Парсим теги
        tags_str = self.tags_var.get().strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        self.result = {
            'name': name,
            'icon': self.icon_var.get(),
            'category': self.category_var.get(),
            'tags': tags,
            'description': self.desc_text.get("1.0", tk.END).strip()
        }
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


class ArtifactBrowserDialog:
    """Браузер артефактов для выбора и размещения"""

    def __init__(self, parent, artifact_manager):
        self.artifact_manager = artifact_manager
        self.result = None
        self.selected_artifact = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Библиотека заготовок")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.configure(bg="#2a2a2a")
        
        self._build_ui()
        self._load_artifacts()
        self.dialog.wait_window()

    def _build_ui(self):
        # Заголовок
        header = tk.Frame(self.dialog, bg="#2a2a2a")
        header.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(
            header,
            text="📚 Библиотека заготовок",
            font=("Arial", 14, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        # Поиск
        search_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        search_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            bg="#2a2a2a",
            fg="#888888"
        ).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_artifacts())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=4)
        
        # Основная область
        main_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Левая панель - категории
        left_panel = tk.Frame(main_frame, bg="#353535", width=150)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(
            left_panel,
            text="Категории",
            font=("Arial", 10, "bold"),
            bg="#353535",
            fg="#aaaaaa"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.category_listbox = tk.Listbox(
            left_panel,
            bg="#353535",
            fg="#ffffff",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            font=("Arial", 10),
            borderwidth=0,
            highlightthickness=0
        )
        self.category_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', lambda e: self._filter_artifacts())
        
        # Добавляем категории
        self.category_listbox.insert(tk.END, "🗂 Все")
        for cat in SaveArtifactDialog.CATEGORIES:
            self.category_listbox.insert(tk.END, f"  {cat}")
        self.category_listbox.selection_set(0)
        
        # Правая панель - артефакты
        right_panel = tk.Frame(main_frame, bg="#2a2a2a")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Скролл для карточек
        canvas_frame = tk.Frame(right_panel, bg="#2a2a2a")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.artifacts_canvas = tk.Canvas(
            canvas_frame,
            bg="#2a2a2a",
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.artifacts_canvas.yview)
        
        self.artifacts_frame = tk.Frame(self.artifacts_canvas, bg="#2a2a2a")
        
        self.artifacts_canvas.create_window((0, 0), window=self.artifacts_frame, anchor="nw")
        self.artifacts_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.artifacts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.artifacts_frame.bind('<Configure>', 
            lambda e: self.artifacts_canvas.configure(scrollregion=self.artifacts_canvas.bbox("all")))
        
        # Привязка колеса мыши
        self.artifacts_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Панель информации
        info_panel = tk.Frame(self.dialog, bg="#353535", height=80)
        info_panel.pack(fill=tk.X, padx=15, pady=(0, 10))
        info_panel.pack_propagate(False)
        
        self.info_label = tk.Label(
            info_panel,
            text="Выберите заготовку для просмотра информации",
            font=("Arial", 10),
            bg="#353535",
            fg="#888888",
            wraplength=550,
            justify=tk.LEFT
        )
        self.info_label.pack(anchor="w", padx=10, pady=10)
        
        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.place_btn = tk.Button(
            btn_frame,
            text="Разместить",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            state=tk.DISABLED,
            command=self._on_place
        )
        self.place_btn.pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Удалить",
            font=("Arial", 11),
            bg="#aa3333",
            fg="#ffffff",
            activebackground="#cc4444",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_delete
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Закрыть",
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_close
        ).pack(side=tk.RIGHT)
        
        # Горячие клавиши
        self.dialog.bind('<Escape>', lambda e: self._on_close())
        self.dialog.bind('<Return>', lambda e: self._on_place())

    def _on_mousewheel(self, event):
        self.artifacts_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_artifacts(self):
        """Загружает и отображает артефакты"""
        self._filter_artifacts()

    def _filter_artifacts(self):
        """Фильтрует артефакты по категории и поиску"""
        # Очищаем
        for widget in self.artifacts_frame.winfo_children():
            widget.destroy()
        
        # Получаем фильтры
        search_query = self.search_var.get().lower()
        
        category_sel = self.category_listbox.curselection()
        if category_sel:
            cat_text = self.category_listbox.get(category_sel[0])
            if "Все" in cat_text:
                category = None
            else:
                category = cat_text.strip()
        else:
            category = None
        
        # Фильтруем
        artifacts = self.artifact_manager.get_all_artifacts()
        
        if category:
            artifacts = [a for a in artifacts if a.category == category]
        
        if search_query:
            artifacts = [a for a in artifacts if 
                search_query in a.name.lower() or
                search_query in a.description.lower() or
                any(search_query in t.lower() for t in a.tags)
            ]
        
        # Отображаем карточки
        row = 0
        col = 0
        max_cols = 3
        
        for artifact in artifacts:
            card = self._create_artifact_card(artifact)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if not artifacts:
            tk.Label(
                self.artifacts_frame,
                text="Нет заготовок",
                font=("Arial", 11),
                bg="#2a2a2a",
                fg="#666666"
            ).grid(row=0, column=0, pady=50)

    def _create_artifact_card(self, artifact):
        """Создаёт карточку артефакта"""
        card = tk.Frame(
            self.artifacts_frame,
            bg="#3a3a3a",
            relief=tk.FLAT,
            borderwidth=0
        )
        card.configure(width=150, height=120)
        card.pack_propagate(False)
        
        # Иконка
        icon_label = tk.Label(
            card,
            text=artifact.icon,
            font=("Arial", 24),
            bg="#3a3a3a",
            fg="#ffffff"
        )
        icon_label.pack(pady=(15, 5))
        
        # Название
        name_label = tk.Label(
            card,
            text=artifact.name[:15] + "..." if len(artifact.name) > 15 else artifact.name,
            font=("Arial", 10, "bold"),
            bg="#3a3a3a",
            fg="#ffffff"
        )
        name_label.pack()
        
        # Информация
        info_text = f"{len(artifact.elements)} эл. | {len(artifact.mechanisms)} мех."
        info_label = tk.Label(
            card,
            text=info_text,
            font=("Arial", 8),
            bg="#3a3a3a",
            fg="#888888"
        )
        info_label.pack(pady=(2, 0))
        
        # События
        def on_enter(e):
            card.configure(bg="#4a4a4a")
            for child in card.winfo_children():
                child.configure(bg="#4a4a4a")
        
        def on_leave(e):
            bg = "#0078d4" if self.selected_artifact == artifact else "#3a3a3a"
            card.configure(bg=bg)
            for child in card.winfo_children():
                child.configure(bg=bg)
        
        def on_click(e):
            self._select_artifact(artifact, card)
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        card.bind('<Button-1>', on_click)
        
        for child in card.winfo_children():
            child.bind('<Button-1>', on_click)
        
        return card

    def _select_artifact(self, artifact, card):
        """Выбирает артефакт"""
        # Сбрасываем предыдущий выбор
        for child in self.artifacts_frame.winfo_children():
            child.configure(bg="#3a3a3a")
            for c in child.winfo_children():
                c.configure(bg="#3a3a3a")
        
        # Выделяем текущий
        self.selected_artifact = artifact
        card.configure(bg="#0078d4")
        for child in card.winfo_children():
            child.configure(bg="#0078d4")
        
        # Обновляем информацию
        info = f"{artifact.icon} {artifact.name}\n"
        info += f"Категория: {artifact.category}\n"
        info += f"Элементов: {len(artifact.elements)} | Механизмов: {len(artifact.mechanisms)}\n"
        if artifact.description:
            info += f"\n{artifact.description}"
        if artifact.tags:
            info += f"\n\nТеги: {', '.join(artifact.tags)}"
        
        self.info_label.config(text=info)
        self.place_btn.config(state=tk.NORMAL)

    def _on_place(self):
        """Размещает выбранный артефакт"""
        if self.selected_artifact:
            self.result = self.selected_artifact
            self.dialog.destroy()

    def _on_delete(self):
        """Удаляет выбранный артефакт"""
        if not self.selected_artifact:
            return
        
        if messagebox.askyesno("Удаление", f"Удалить заготовку '{self.selected_artifact.name}'?"):
            self.artifact_manager.delete_artifact(self.selected_artifact.id)
            self.selected_artifact = None
            self.place_btn.config(state=tk.DISABLED)
            self.info_label.config(text="Выберите заготовку для просмотра информации")
            self._filter_artifacts()

    def _on_close(self):
        self.dialog.destroy()


def show_save_artifact_dialog(parent, element_count=0, mechanism_count=0):
    """Показывает диалог сохранения артефакта"""
    dialog = SaveArtifactDialog(parent, element_count, mechanism_count)
    return dialog.result


def show_artifact_browser(parent, artifact_manager):
    """Показывает браузер артефактов"""
    dialog = ArtifactBrowserDialog(parent, artifact_manager)
    return dialog.result

