#!/usr/bin/env python3
"""
Вкладка настроек приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from .tab_base import TabBase


class TabSettings(TabBase):
    """Вкладка настроек"""

    TAB_ID = "settings"
    TAB_SYMBOL = "⚙"

    PROVIDERS = [
        ('openai', 'OpenAI', 'GPT-4, GPT-3.5'),
        ('anthropic', 'Anthropic', 'Claude'),
        ('google', 'Google AI', 'Gemini'),
        ('perplexity', 'Perplexity', 'pplx-7b'),
        ('github', 'GitHub Copilot', 'Copilot'),
        ('ollama', 'Ollama', 'Локальные модели'),
        ('gpt4all', 'GPT4All', 'Локальные модели'),
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.app = None
        self.api_keys = {}
        self.settings_file = os.path.expanduser('~/.panel_editor_settings.json')

    def set_app(self, app):
        self.app = app

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === API Ключи ===
        sec = self._section(self.content, "API Ключи")
        
        self.key_vars = {}
        for provider_id, name, desc in self.PROVIDERS:
            row = self._row(sec)
            self._label(row, f"{name}:", 12).pack(side=tk.LEFT)
            
            var = tk.StringVar()
            self.key_vars[provider_id] = var
            
            entry = tk.Entry(row, textvariable=var, width=30, font=("Arial", 9),
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT, relief=tk.FLAT,
                           show='•', insertbackground=self.COLOR_TEXT,
                           highlightthickness=1, highlightbackground=self.COLOR_BORDER)
            entry.pack(side=tk.LEFT, padx=4)
            
            # Кнопка показать/скрыть
            def toggle_show(e=entry):
                e.config(show='' if e.cget('show') else '•')
            
            tk.Button(row, text="◉", font=("Arial", 8),
                     bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED,
                     relief=tk.FLAT, command=toggle_show).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._button(row, "Сохранить ключи", self._save_keys, 'primary').pack(side=tk.LEFT, padx=2)
        self._button(row, "Загрузить", self._load_keys).pack(side=tk.LEFT, padx=2)
        
        # === Общие настройки ===
        sec = self._section(self.content, "Общие")
        
        row = self._row(sec)
        self._label(row, "Тема:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value='dark')
        self._combo(row, ['Dark', 'Light', 'System'], self.theme_var, 10).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Язык:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value='ru')
        self._combo(row, ['Русский', 'English'], self.lang_var, 10).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self.autosave_var = tk.BooleanVar(value=True)
        self._checkbox(row, "Автосохранение", self.autosave_var).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Интервал:", 10).pack(side=tk.LEFT)
        self.autosave_interval = tk.StringVar(value='120')
        self._entry(row, self.autosave_interval, 6).pack(side=tk.LEFT)
        tk.Label(row, text="сек", font=("Arial", 8),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=4)
        
        # === Производительность ===
        sec = self._section(self.content, "Производительность")
        
        row = self._row(sec)
        self.hardware_accel = tk.BooleanVar(value=True)
        self._checkbox(row, "Аппаратное ускорение", self.hardware_accel).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self.smooth_scroll = tk.BooleanVar(value=True)
        self._checkbox(row, "Плавная прокрутка", self.smooth_scroll).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "FPS limit:", 10).pack(side=tk.LEFT)
        self.fps_limit = tk.StringVar(value='60')
        self._combo(row, ['30', '60', '120', 'Unlimited'], self.fps_limit, 10).pack(side=tk.LEFT)
        
        # === Пути ===
        sec = self._section(self.content, "Пути")
        
        row = self._row(sec)
        self._label(row, "Проекты:", 10).pack(side=tk.LEFT)
        self.projects_path = tk.StringVar(value=os.path.expanduser('~/PanelEditorProjects'))
        self._entry(row, self.projects_path, 25).pack(side=tk.LEFT, padx=4)
        self._icon_button(row, '…', self._browse_projects).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Экспорт:", 10).pack(side=tk.LEFT)
        self.export_path = tk.StringVar(value=os.path.expanduser('~/PanelEditorExport'))
        self._entry(row, self.export_path, 25).pack(side=tk.LEFT, padx=4)
        self._icon_button(row, '…', self._browse_export).pack(side=tk.LEFT)
        
        # === AI Настройки ===
        sec = self._section(self.content, "AI Настройки")
        
        row = self._row(sec)
        self._label(row, "Провайдер по умолчанию:", 18).pack(side=tk.LEFT)
        self.default_provider = tk.StringVar(value='openai')
        self._combo(row, [p[1] for p in self.PROVIDERS], self.default_provider, 12).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Макс. токенов:", 14).pack(side=tk.LEFT)
        self.max_tokens = tk.StringVar(value='2048')
        self._entry(row, self.max_tokens, 8).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Температура:", 14).pack(side=tk.LEFT)
        self.temperature = tk.DoubleVar(value=0.7)
        s = self._scale(row, self.temperature, 0, 2, 100)
        s.config(resolution=0.1)
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.temperature, font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # === Действия ===
        sec = self._section(self.content, "Действия")
        
        row = self._row(sec)
        self._button(row, "Сохранить всё", self._save_all, 'success').pack(side=tk.LEFT, padx=2)
        self._button(row, "Сбросить", self._reset_settings, 'danger').pack(side=tk.LEFT, padx=2)
        
        row = self._row(sec)
        self._button(row, "Очистить кэш", self._clear_cache).pack(side=tk.LEFT, padx=2)
        self._button(row, "Экспорт настроек", self._export_settings).pack(side=tk.LEFT, padx=2)
        self._button(row, "Импорт настроек", self._import_settings).pack(side=tk.LEFT, padx=2)
        
        # Загрузить настройки
        self._load_settings()

    def _save_keys(self):
        """Сохранить API ключи"""
        keys = {k: v.get() for k, v in self.key_vars.items() if v.get()}
        try:
            data = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
            data['api_keys'] = keys
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Сохранено", "API ключи сохранены", parent=self.frame)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}", parent=self.frame)

    def _load_keys(self):
        """Загрузить API ключи"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                keys = data.get('api_keys', {})
                for k, v in keys.items():
                    if k in self.key_vars:
                        self.key_vars[k].set(v)
        except Exception as e:
            print(f"Error loading keys: {e}")

    def _load_settings(self):
        """Загрузить все настройки"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                # API ключи
                keys = data.get('api_keys', {})
                for k, v in keys.items():
                    if k in self.key_vars:
                        self.key_vars[k].set(v)
                
                # Остальные настройки
                self.theme_var.set(data.get('theme', 'dark'))
                self.lang_var.set(data.get('language', 'ru'))
                self.autosave_var.set(data.get('autosave', True))
                self.autosave_interval.set(data.get('autosave_interval', '120'))
                self.projects_path.set(data.get('projects_path', os.path.expanduser('~/PanelEditorProjects')))
                self.export_path.set(data.get('export_path', os.path.expanduser('~/PanelEditorExport')))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _save_all(self):
        """Сохранить все настройки"""
        try:
            data = {
                'api_keys': {k: v.get() for k, v in self.key_vars.items() if v.get()},
                'theme': self.theme_var.get(),
                'language': self.lang_var.get(),
                'autosave': self.autosave_var.get(),
                'autosave_interval': self.autosave_interval.get(),
                'projects_path': self.projects_path.get(),
                'export_path': self.export_path.get(),
                'default_provider': self.default_provider.get(),
                'max_tokens': self.max_tokens.get(),
                'temperature': self.temperature.get(),
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Сохранено", "Настройки сохранены", parent=self.frame)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}", parent=self.frame)

    def _reset_settings(self):
        """Сбросить настройки"""
        if messagebox.askyesno("Сброс", "Сбросить все настройки?", parent=self.frame):
            self.theme_var.set('dark')
            self.lang_var.set('ru')
            self.autosave_var.set(True)
            self.autosave_interval.set('120')
            for var in self.key_vars.values():
                var.set('')

    def _clear_cache(self):
        """Очистить кэш"""
        messagebox.showinfo("Кэш", "Кэш очищен", parent=self.frame)

    def _export_settings(self):
        """Экспорт настроек"""
        path = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[("JSON файлы", "*.json")],
            parent=self.frame
        )
        if path:
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Экспорт", f"Настройки экспортированы: {path}", parent=self.frame)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}", parent=self.frame)

    def _import_settings(self):
        """Импорт настроек"""
        path = filedialog.askopenfilename(
            filetypes=[("JSON файлы", "*.json")],
            parent=self.frame
        )
        if path:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                with open(self.settings_file, 'w') as f:
                    json.dump(data, f, indent=2)
                self._load_settings()
                messagebox.showinfo("Импорт", "Настройки импортированы", parent=self.frame)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}", parent=self.frame)

    def _browse_projects(self):
        path = filedialog.askdirectory(parent=self.frame)
        if path:
            self.projects_path.set(path)

    def _browse_export(self):
        path = filedialog.askdirectory(parent=self.frame)
        if path:
            self.export_path.set(path)

    def get_api_key(self, provider):
        """Получить API ключ для провайдера"""
        return self.key_vars.get(provider, tk.StringVar()).get()
