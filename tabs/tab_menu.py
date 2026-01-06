#!/usr/bin/env python3
"""
Вкладка меню - управление проектами и артефактами
"""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from .tab_base import TabBase


class TabMenu(TabBase):
    """Вкладка меню"""

    TAB_ID = "menu"
    TAB_SYMBOL = "≡"

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.project_manager = None
        self.artifact_manager = None
        self.app = None

    def set_project_manager(self, manager):
        self.project_manager = manager

    def set_artifact_manager(self, manager):
        self.artifact_manager = manager

    def set_app(self, app):
        self.app = app

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Проект ===
        sec = self._section(self.content, "Текущий проект")
        
        self.project_lbl = tk.Label(sec, text="Без названия", font=("Arial", 10, "bold"),
                                   bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_ACCENT)
        self.project_lbl.pack(anchor="w")
        
        row = self._row(sec)
        self._button(row, "Создать", self._new_project, 'success').pack(side=tk.LEFT, padx=2)
        self._button(row, "Открыть", self._open_project).pack(side=tk.LEFT, padx=2)
        self._button(row, "Сохранить", self._save_project, 'primary').pack(side=tk.LEFT, padx=2)
        
        row = self._row(sec)
        self._button(row, "Сохранить как...", self._save_as).pack(side=tk.LEFT, padx=2)
        self._button(row, "Переименовать", self._rename_project).pack(side=tk.LEFT, padx=2)
        
        # === Список проектов ===
        sec = self._section(self.content, "Проекты")
        
        # Поиск
        row = self._row(sec)
        self.search_var = tk.StringVar()
        search_entry = self._entry(row, self.search_var, 20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self._filter_projects())
        
        self._icon_button(row, '⟳', self._refresh_projects).pack(side=tk.RIGHT)
        
        # Список
        self.projects_list = tk.Listbox(sec, height=8, font=("Arial", 9),
                                       bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                       selectbackground=self.COLOR_ACCENT,
                                       selectforeground='#fff', relief=tk.FLAT,
                                       highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.projects_list.pack(fill=tk.BOTH, expand=True, pady=4)
        self.projects_list.bind('<<ListboxSelect>>', self._on_project_select)
        self.projects_list.bind('<Double-Button-1>', lambda e: self._open_selected())
        
        # Скролл
        self.projects_list.bind('<Button-4>', lambda e: self.projects_list.yview_scroll(-2, 'units'))
        self.projects_list.bind('<Button-5>', lambda e: self.projects_list.yview_scroll(2, 'units'))
        
        row = self._row(sec)
        self._button(row, "Открыть", self._open_selected).pack(side=tk.LEFT, padx=2)
        self._button(row, "Удалить", self._delete_project, 'danger').pack(side=tk.LEFT, padx=2)
        
        # === Артефакты ===
        sec = self._section(self.content, "Артефакты (шаблоны)")
        
        self.artifacts_list = tk.Listbox(sec, height=6, font=("Arial", 9),
                                        bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                        selectbackground=self.COLOR_ACCENT,
                                        selectforeground='#fff', relief=tk.FLAT,
                                        highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.artifacts_list.pack(fill=tk.BOTH, expand=True, pady=4)
        
        row = self._row(sec)
        self._button(row, "Применить", self._apply_artifact).pack(side=tk.LEFT, padx=2)
        self._button(row, "Сохранить выбранное", self._save_artifact, 'primary').pack(side=tk.LEFT, padx=2)
        self._button(row, "Удалить", self._delete_artifact, 'danger').pack(side=tk.LEFT, padx=2)
        
        # === Экспорт ===
        sec = self._section(self.content, "Экспорт")
        
        row = self._row(sec)
        self._button(row, "HTML/CSS", self._export_html).pack(side=tk.LEFT, padx=2)
        self._button(row, "PNG", self._export_png).pack(side=tk.LEFT, padx=2)
        self._button(row, "JSON", self._export_json).pack(side=tk.LEFT, padx=2)
        
        # Загрузить данные
        self._refresh_projects()
        self._refresh_artifacts()

    def _new_project(self):
        name = simpledialog.askstring("Новый проект", "Название проекта:",
                                     parent=self.frame)
        if name and self.project_manager:
            self.project_manager.create_project(name)
            self.project_lbl.config(text=name)
            self._refresh_projects()

    def _open_project(self):
        if self.project_manager:
            project = self.project_manager.open_dialog()
            if project:
                self.project_lbl.config(text=project.get('name', 'Проект'))

    def _save_project(self):
        if self.project_manager and self.app:
            self.app.save_project()
            messagebox.showinfo("Сохранено", "Проект сохранён", parent=self.frame)

    def _save_as(self):
        name = simpledialog.askstring("Сохранить как", "Название проекта:",
                                     parent=self.frame)
        if name and self.project_manager:
            self.project_manager.save_as(name)
            self.project_lbl.config(text=name)
            self._refresh_projects()

    def _rename_project(self):
        name = simpledialog.askstring("Переименовать", "Новое название:",
                                     parent=self.frame)
        if name and self.project_manager:
            self.project_manager.rename_current(name)
            self.project_lbl.config(text=name)
            self._refresh_projects()

    def _refresh_projects(self):
        self.projects_list.delete(0, tk.END)
        if self.project_manager:
            for project in self.project_manager.get_all_projects():
                self.projects_list.insert(tk.END, project.get('name', 'Без названия'))

    def _filter_projects(self):
        query = self.search_var.get().lower()
        self.projects_list.delete(0, tk.END)
        if self.project_manager:
            for project in self.project_manager.get_all_projects():
                name = project.get('name', '')
                if query in name.lower():
                    self.projects_list.insert(tk.END, name)

    def _on_project_select(self, e=None):
        pass  # Можно показать превью

    def _open_selected(self):
        sel = self.projects_list.curselection()
        if sel and self.project_manager:
            name = self.projects_list.get(sel[0])
            self.project_manager.load_project(name)
            self.project_lbl.config(text=name)

    def _delete_project(self):
        sel = self.projects_list.curselection()
        if sel and self.project_manager:
            name = self.projects_list.get(sel[0])
            if messagebox.askyesno("Удаление", f"Удалить проект '{name}'?", parent=self.frame):
                self.project_manager.delete_project(name)
                self._refresh_projects()

    def _refresh_artifacts(self):
        self.artifacts_list.delete(0, tk.END)
        if self.artifact_manager:
            for artifact in self.artifact_manager.get_all():
                self.artifacts_list.insert(tk.END, artifact.get('name', 'Артефакт'))

    def _apply_artifact(self):
        sel = self.artifacts_list.curselection()
        if sel and self.artifact_manager:
            name = self.artifacts_list.get(sel[0])
            self.artifact_manager.apply(name)

    def _save_artifact(self):
        if self.app and self.artifact_manager:
            name = simpledialog.askstring("Сохранить артефакт", "Название:",
                                         parent=self.frame)
            if name:
                self.artifact_manager.save_selected(name)
                self._refresh_artifacts()

    def _delete_artifact(self):
        sel = self.artifacts_list.curselection()
        if sel and self.artifact_manager:
            name = self.artifacts_list.get(sel[0])
            if messagebox.askyesno("Удаление", f"Удалить артефакт '{name}'?", parent=self.frame):
                self.artifact_manager.delete(name)
                self._refresh_artifacts()

    def _export_html(self):
        if self.app:
            self.app.export_html()

    def _export_png(self):
        if self.app:
            self.app.export_png()

    def _export_json(self):
        if self.app:
            self.app.export_json()

    def on_activate(self):
        self._refresh_projects()
        self._refresh_artifacts()
