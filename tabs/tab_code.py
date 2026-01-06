#!/usr/bin/env python3
"""
Вкладка генерации кода и экспорта проектов
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
from .tab_base import TabBase
from ..live_project_manager import get_live_project_manager
from ..utils.event_bus import event_bus, on as subscribe


class TabCode(TabBase):
    """Вкладка кода и экспорта проектов"""

    TAB_ID = "code"
    TAB_SYMBOL = "</>"

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.element_manager = None
        self.main_canvas = None
        self.code_generator = None
        self.live_project_manager = get_live_project_manager(config)
        self.auto_update_enabled = True
        
        # Подписка на события обновления кода
        subscribe('project.code_updated', self._on_code_updated)

    def set_element_manager(self, manager):
        self.element_manager = manager

    def set_main_canvas(self, canvas):
        self.main_canvas = canvas

    def set_code_generator(self, generator):
        self.code_generator = generator

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Тип кода ===
        sec = self._section(self.content, "Генерация кода")
        
        row = self._row(sec)
        self.code_type = tk.StringVar(value='html')
        for val, txt in [('html', 'HTML'), ('css', 'CSS'), ('js', 'JS'), ('react', 'React')]:
            tk.Radiobutton(row, text=txt, variable=self.code_type, value=val,
                          font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY
                          ).pack(side=tk.LEFT, padx=4)
        
        row = self._row(sec)
        self._button(row, "Генерировать", self._generate, 'primary').pack(side=tk.LEFT, padx=2)
        self._button(row, "Генерировать всё", self._generate_all, 'success').pack(side=tk.LEFT, padx=2)
        
        # === Редактор кода ===
        sec = self._section(self.content, "Код")
        
        # Тулбар
        toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        
        self._icon_button(toolbar, '⧉', self._copy_code).pack(side=tk.LEFT, padx=1)
        self._tooltip(self._icon_button(toolbar, '⧉', self._copy_code), "Копировать")
        
        self._icon_button(toolbar, '↓', self._save_code).pack(side=tk.LEFT, padx=1)
        self._icon_button(toolbar, '⟳', self._clear_code).pack(side=tk.RIGHT, padx=1)
        
        # Текстовое поле
        code_frame = tk.Frame(sec, bg=self.COLOR_BG)
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        self.code_text = tk.Text(code_frame, font=("Consolas", 10),
                                bg=self.COLOR_BG, fg='#79c0ff',
                                insertbackground=self.COLOR_TEXT, relief=tk.FLAT,
                                wrap=tk.NONE, height=15)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Скролл
        self.code_text.bind('<Button-4>', lambda e: self.code_text.yview_scroll(-2, 'units'))
        self.code_text.bind('<Button-5>', lambda e: self.code_text.yview_scroll(2, 'units'))
        
        # Подсветка синтаксиса
        self.code_text.tag_configure('tag', foreground='#7ee787')
        self.code_text.tag_configure('attr', foreground='#79c0ff')
        self.code_text.tag_configure('value', foreground='#a5d6ff')
        self.code_text.tag_configure('comment', foreground='#8b949e')
        
        # === Опции ===
        sec = self._section(self.content, "Опции")
        
        row = self._row(sec)
        self.minify_var = tk.BooleanVar(value=False)
        self._checkbox(row, "Минификация", self.minify_var).pack(side=tk.LEFT)
        
        self.comments_var = tk.BooleanVar(value=True)
        self._checkbox(row, "Комментарии", self.comments_var).pack(side=tk.LEFT, padx=(8, 0))
        
        row = self._row(sec)
        self.responsive_var = tk.BooleanVar(value=True)
        self._checkbox(row, "Адаптивность", self.responsive_var).pack(side=tk.LEFT)
        
        self.bem_var = tk.BooleanVar(value=False)
        self._checkbox(row, "BEM именование", self.bem_var).pack(side=tk.LEFT, padx=(8, 0))
        
        # === Превью ===
        sec = self._section(self.content, "Превью")
        
        row = self._row(sec)
        self._button(row, "Открыть в браузере", self._preview_browser).pack(side=tk.LEFT, padx=2)
        self._button(row, "Встроенное превью", self._preview_inline).pack(side=tk.LEFT, padx=2)
        
        # === Live Project ===
        sec = self._section(self.content, "Живой проект")
        
        # Автообновление
        row = self._row(sec)
        self.auto_update_var = tk.BooleanVar(value=True)
        cb = self._checkbox(row, "Автообновление кода", self.auto_update_var)
        cb.config(command=self._toggle_auto_update)
        cb.pack(side=tk.LEFT)
        
        self.live_status_lbl = tk.Label(row, text="● Активно", font=("Arial", 9),
                                       bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_SUCCESS)
        self.live_status_lbl.pack(side=tk.RIGHT)
        
        # Папка проекта
        row = self._row(sec)
        self._label(row, "Папка:").pack(side=tk.LEFT)
        self.project_path_var = tk.StringVar(value="./projects/current")
        path_entry = self._entry(row, self.project_path_var, 20)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        
        browse_btn = tk.Button(row, text="📁", font=("Arial", 10),
                              bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                              relief=tk.FLAT, cursor="hand2",
                              command=self._browse_project_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        # Кнопки управления проектом  
        row = self._row(sec)
        self._button(row, "Инициализировать", self._init_project, 'primary').pack(side=tk.LEFT, padx=2)
        self._button(row, "Обновить код", self._force_update, 'secondary').pack(side=tk.LEFT, padx=2)
        
        # === Экспорт ===
        sec = self._section(self.content, "Экспорт проекта")
        
        # Выбор формата
        row = self._row(sec)
        self._label(row, "Формат:").pack(side=tk.LEFT)
        self.export_format = tk.StringVar(value='html')
        formats = [('html', 'HTML/CSS'), ('react', 'React'), ('vue', 'Vue.js')]
        
        for val, txt in formats:
            tk.Radiobutton(row, text=txt, variable=self.export_format, value=val,
                          font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY
                          ).pack(side=tk.LEFT, padx=4)
        
        # Кнопки экспорта
        row = self._row(sec)
        self._button(row, "📁 Экспорт в папку", self._export_to_folder, 'success').pack(side=tk.LEFT, padx=2)
        self._button(row, "📦 Создать ZIP", self._export_to_zip, 'success').pack(side=tk.LEFT, padx=2)
        
        # Статистика проекта
        row = self._row(sec)
        self.stats_lbl = tk.Label(row, text="Элементов: 0, Строк кода: 0",
                                 font=("Arial", 8), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED)
        self.stats_lbl.pack(side=tk.LEFT)
        
        # Инициализация Live Project Manager
        if self.live_project_manager:
            project_path = os.path.abspath(self.project_path_var.get())
            self.live_project_manager.set_project_directory(project_path)

    def _generate(self):
        """Генерировать код для выбранного элемента"""
        if not self.element_manager:
            return
        
        elem = self.element_manager.selected_element
        if not elem:
            messagebox.showwarning("Внимание", "Выберите элемент", parent=self.frame)
            return
        
        code_type = self.code_type.get()
        code = self._generate_element_code(elem, code_type)
        
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', code)
        self._highlight_syntax()

    def _generate_all(self):
        """Генерировать код для всего интерфейса"""
        if not self.element_manager or not self.main_canvas:
            return
        
        code_type = self.code_type.get()
        
        if code_type == 'html':
            code = self._generate_html()
        elif code_type == 'css':
            code = self._generate_css()
        elif code_type == 'js':
            code = self._generate_js()
        elif code_type == 'react':
            code = self._generate_react()
        else:
            code = "// Неизвестный тип"
        
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', code)
        self._highlight_syntax()

    def _generate_element_code(self, elem, code_type):
        """Генерирует код для элемента"""
        etype = getattr(elem, 'ELEMENT_TYPE', 'div')
        
        if code_type == 'html':
            return f'''<div class="{etype}" style="
    position: absolute;
    left: {int(elem.x)}px;
    top: {int(elem.y)}px;
    width: {int(elem.width)}px;
    height: {int(elem.height)}px;
"></div>'''
        
        elif code_type == 'css':
            return f'''.{etype} {{
    position: absolute;
    left: {int(elem.x)}px;
    top: {int(elem.y)}px;
    width: {int(elem.width)}px;
    height: {int(elem.height)}px;
    background: {elem.properties.get('fill_color', '#161b22')};
    border: {elem.properties.get('stroke_width', 1)}px solid {elem.properties.get('stroke_color', '#30363d')};
    border-radius: {elem.properties.get('corner_radius', 0)}px;
}}'''
        
        elif code_type == 'react':
            return f'''const {etype.capitalize()} = () => (
    <div style={{{{
        position: 'absolute',
        left: {int(elem.x)},
        top: {int(elem.y)},
        width: {int(elem.width)},
        height: {int(elem.height)},
    }}}} />
);'''
        
        return f"// Код для {etype}"

    def _generate_html(self):
        """Генерирует HTML"""
        elements = self.element_manager.get_all_elements()
        canvas = self.main_canvas
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Interface</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container" style="width: {int(canvas.width)}px; height: {int(canvas.height)}px;">
'''
        
        for elem in elements:
            etype = getattr(elem, 'ELEMENT_TYPE', 'div')
            html += f'        <div class="{etype}" id="{elem.id[:8]}"></div>\n'
        
        html += '''    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        return html
    
    # === Новые методы для Live Project ===
    
    def _on_code_updated(self, event_data=None):
        """Обработчик обновления кода"""
        if self.auto_update_enabled and self.code_type.get() in ['html', 'css', 'js']:
            self._update_code_display()
        self._update_stats()
    
    def _toggle_auto_update(self):
        """Переключает автообновление"""
        enabled = self.auto_update_var.get()
        self.auto_update_enabled = enabled
        
        if self.live_project_manager:
            self.live_project_manager.enable_auto_generation(enabled)
        
        status_text = "● Активно" if enabled else "○ Отключено"
        status_color = self.COLOR_SUCCESS if enabled else self.COLOR_TEXT_MUTED
        self.live_status_lbl.config(text=status_text, fg=status_color)
        
        if enabled:
            self._update_code_display()
    
    def _update_code_display(self):
        """Обновляет отображение кода в редакторе"""
        if not self.live_project_manager:
            return
        
        code_type = self.code_type.get()
        
        try:
            if code_type == 'html':
                code = self.live_project_manager.get_generated_html()
            elif code_type == 'css':
                code = self.live_project_manager.get_generated_css()
            elif code_type == 'js':
                code = self.live_project_manager.get_generated_js()
            else:
                return
            
            # Обновляем только если изменился
            current_code = self.code_text.get('1.0', 'end-1c')
            if current_code != code:
                self.code_text.delete('1.0', tk.END)
                self.code_text.insert('1.0', code)
                self._highlight_syntax()
                
        except Exception as e:
            print(f"[TabCode] Ошибка обновления кода: {e}")
    
    def _update_stats(self):
        """Обновляет статистику проекта"""
        if not self.live_project_manager:
            return
        
        try:
            stats = self.live_project_manager.get_project_stats()
            elements = stats.get('elements_count', 0)
            lines = sum(stats.get('lines_of_code', {}).values())
            
            self.stats_lbl.config(text=f"Элементов: {elements}, Строк кода: {lines}")
            
        except Exception as e:
            print(f"[TabCode] Ошибка обновления статистики: {e}")
    
    def _browse_project_folder(self):
        """Выбор папки проекта"""
        folder = filedialog.askdirectory(
            title="Выберите папку проекта",
            initialdir=os.path.dirname(self.project_path_var.get())
        )
        
        if folder:
            self.project_path_var.set(folder)
            if self.live_project_manager:
                self.live_project_manager.set_project_directory(folder)
    
    def _init_project(self):
        """Инициализирует живой проект"""
        if not self.live_project_manager:
            return
        
        project_path = os.path.abspath(self.project_path_var.get())
        
        try:
            # Устанавливаем менеджеры
            self.live_project_manager.set_managers(self.element_manager, self.main_canvas)
            self.live_project_manager.set_project_directory(project_path)
            self.live_project_manager.enable_auto_generation(True)
            
            # Принудительно генерируем код
            self.live_project_manager._regenerate_code()
            
            messagebox.showinfo("Успех", 
                               f"Проект инициализирован в:\n{project_path}\n\n"
                               f"Файлы будут обновляться автоматически.",
                               parent=self.frame)
            
            self._update_code_display()
            self._update_stats()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось инициализировать проект:\n{e}", parent=self.frame)
    
    def _force_update(self):
        """Принудительно обновляет код"""
        if not self.live_project_manager:
            return
        
        try:
            self.live_project_manager._invalidate_cache()
            self.live_project_manager._regenerate_code()
            self._update_code_display()
            self._update_stats()
            
            messagebox.showinfo("Обновлено", "Код успешно обновлён", parent=self.frame)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить код:\n{e}", parent=self.frame)
    
    def _export_to_folder(self):
        """Экспорт проекта в папку"""
        if not self.live_project_manager:
            return
        
        export_dir = filedialog.askdirectory(
            title="Выберите папку для экспорта"
        )
        
        if not export_dir:
            return
        
        format_name = self.export_format.get()
        
        try:
            # Обновляем менеджеры
            self.live_project_manager.set_managers(self.element_manager, self.main_canvas)
            
            # Экспортируем
            result_path = self.live_project_manager.export_project(export_dir, format_name)
            
            # Спрашиваем об открытии папки
            open_folder = messagebox.askyesno("Экспорт завершён",
                                            f"Проект экспортирован в:\n{result_path}\n\n"
                                            f"Открыть папку?",
                                            parent=self.frame)
            
            if open_folder:
                self._open_folder(result_path)
                
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", f"Не удалось экспортировать проект:\n{e}", parent=self.frame)
    
    def _export_to_zip(self):
        """Экспорт проекта в ZIP архив"""
        if not self.live_project_manager:
            return
        
        format_name = self.export_format.get()
        default_filename = f"interface-{format_name}.zip"
        
        zip_path = filedialog.asksaveasfilename(
            title="Сохранить ZIP архив",
            defaultextension=".zip",
            filetypes=[("ZIP архивы", "*.zip"), ("Все файлы", "*.*")],
            initialvalue=default_filename
        )
        
        if not zip_path:
            return
        
        try:
            # Обновляем менеджеры
            self.live_project_manager.set_managers(self.element_manager, self.main_canvas)
            
            # Создаём ZIP
            result_path = self.live_project_manager.create_zip_export(zip_path, format_name)
            
            # Спрашиваем об открытии папки
            open_folder = messagebox.askyesno("Экспорт завершён",
                                            f"ZIP архив создан:\n{result_path}\n\n"
                                            f"Открыть папку с файлом?",
                                            parent=self.frame)
            
            if open_folder:
                self._open_folder(os.path.dirname(result_path))
                
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", f"Не удалось создать ZIP:\n{e}", parent=self.frame)
    
    def _open_folder(self, path):
        """Открывает папку в файловом менеджере"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # Linux/Mac
                if os.uname().sysname == 'Darwin':  # Mac
                    subprocess.run(['open', path])
                else:  # Linux
                    subprocess.run(['xdg-open', path])
        except Exception as e:
            print(f"[TabCode] Не удалось открыть папку: {e}")
    
    def set_managers_extended(self, element_manager, main_canvas):
        """Расширенная установка менеджеров"""
        self.set_element_manager(element_manager)
        self.set_main_canvas(main_canvas)
        
        # Обновляем Live Project Manager
        if self.live_project_manager:
            self.live_project_manager.set_managers(element_manager, main_canvas)

    def _generate_css(self):
        """Генерирует CSS"""
        elements = self.element_manager.get_all_elements()
        canvas = self.main_canvas
        
        css = f'''/* Generated CSS */
.container {{
    position: relative;
    width: {int(canvas.width)}px;
    height: {int(canvas.height)}px;
    background: {canvas.properties.get('fill_color', '#0d1117')};
}}

'''
        
        for elem in elements:
            etype = getattr(elem, 'ELEMENT_TYPE', 'div')
            props = getattr(elem, 'properties', {})
            
            css += f'''.{etype}#{elem.id[:8]} {{
    position: absolute;
    left: {int(elem.x)}px;
    top: {int(elem.y)}px;
    width: {int(elem.width)}px;
    height: {int(elem.height)}px;
    background: {props.get('fill_color', 'transparent')};
    border: {props.get('stroke_width', 1)}px solid {props.get('stroke_color', '#30363d')};
    border-radius: {props.get('corner_radius', 0)}px;
}}

'''
        
        return css

    def _generate_js(self):
        """Генерирует JavaScript"""
        return '''// Generated JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('Interface loaded');
    
    // Add event listeners
    document.querySelectorAll('.button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            console.log('Button clicked:', e.target.id);
        });
    });
});'''

    def _generate_react(self):
        """Генерирует React компонент"""
        return '''// Generated React Component
import React from 'react';
import './styles.css';

const Interface = () => {
    return (
        <div className="container">
            {/* Generated elements */}
        </div>
    );
};

export default Interface;'''

    def _highlight_syntax(self):
        """Подсветка синтаксиса"""
        # Простая подсветка
        pass

    def _copy_code(self):
        """Копировать код"""
        code = self.code_text.get('1.0', tk.END)
        self.frame.clipboard_clear()
        self.frame.clipboard_append(code)
        messagebox.showinfo("Скопировано", "Код скопирован в буфер обмена", parent=self.frame)

    def _save_code(self):
        """Сохранить код в файл"""
        code_type = self.code_type.get()
        ext_map = {'html': '.html', 'css': '.css', 'js': '.js', 'react': '.jsx'}
        ext = ext_map.get(code_type, '.txt')
        
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"{code_type.upper()} файлы", f"*{ext}"), ("Все файлы", "*.*")],
            parent=self.frame
        )
        
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.code_text.get('1.0', tk.END))
            messagebox.showinfo("Сохранено", f"Файл сохранён: {path}", parent=self.frame)

    def _clear_code(self):
        """Очистить код"""
        self.code_text.delete('1.0', tk.END)

    def _preview_browser(self):
        """Открыть в браузере"""
        import tempfile
        import webbrowser
        
        html = self._generate_html()
        css = self._generate_css()
        
        full_html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>\n{css}\n</style>')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(full_html)
            webbrowser.open(f'file://{f.name}')

    def _preview_inline(self):
        """Встроенное превью"""
        messagebox.showinfo("Превью", "Встроенное превью в разработке", parent=self.frame)
