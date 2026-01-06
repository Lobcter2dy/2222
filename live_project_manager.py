#!/usr/bin/env python3
"""
Live Project Manager
Система генерации кода в реальном времени и экспорта готовых проектов
"""
import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from .code_generator import CodeGenerator
from .utils.event_bus import event_bus, on as subscribe
from .utils.logger import get_logger

log = get_logger('LiveProjectManager')


class ProjectTemplate:
    """Шаблон проекта для экспорта"""
    
    def __init__(self, name: str, description: str, files: Dict[str, str]):
        self.name = name
        self.description = description
        self.files = files  # Относительный путь -> содержимое файла


class LiveProjectManager:
    """
    Менеджер живых проектов.
    
    Отслеживает изменения элементов и автоматически генерирует код.
    Позволяет экспортировать готовые проекты в различные форматы.
    """
    
    def __init__(self, config):
        self.config = config
        self.code_generator = CodeGenerator()
        
        # Состояние проекта
        self.element_manager = None
        self.main_canvas = None
        self.project_dir = None
        self.auto_generation = True
        
        # Кеш сгенерированного кода
        self._cached_html = ""
        self._cached_css = ""
        self._cached_js = ""
        self._cache_valid = False
        
        # Шаблоны проектов
        self.templates = self._init_templates()
        
        # Подписка на события
        self._setup_event_listeners()
        
        log.info("LiveProjectManager инициализирован")
    
    def _init_templates(self) -> Dict[str, ProjectTemplate]:
        """Инициализирует шаблоны проектов"""
        templates = {}
        
        # Базовый HTML проект
        templates['html'] = ProjectTemplate(
            name="HTML/CSS/JS проект",
            description="Статичный веб-сайт",
            files={
                "index.html": "<!-- Will be generated -->",
                "style.css": "/* Will be generated */",
                "script.js": "// Will be generated",
                "README.md": self._get_readme_template(),
                "package.json": self._get_package_json_template()
            }
        )
        
        # React проект
        templates['react'] = ProjectTemplate(
            name="React приложение",
            description="Modern React app",
            files={
                "src/App.js": "// Will be generated",
                "src/index.js": self._get_react_index_template(),
                "src/App.css": "/* Will be generated */",
                "public/index.html": self._get_react_html_template(),
                "package.json": self._get_react_package_template(),
                "README.md": self._get_readme_template("React")
            }
        )
        
        # Vue проект  
        templates['vue'] = ProjectTemplate(
            name="Vue приложение",
            description="Vue.js app",
            files={
                "src/App.vue": "<!-- Will be generated -->",
                "src/main.js": self._get_vue_main_template(),
                "public/index.html": self._get_vue_html_template(),
                "package.json": self._get_vue_package_template(),
                "README.md": self._get_readme_template("Vue")
            }
        )
        
        return templates
    
    def _setup_event_listeners(self):
        """Настраивает слушатели событий"""
        # События элементов
        subscribe('element.created', self._on_element_changed)
        subscribe('element.updated', self._on_element_changed) 
        subscribe('element.deleted', self._on_element_changed)
        subscribe('element.moved', self._on_element_changed)
        subscribe('element.resized', self._on_element_changed)
        
        # События главной панели
        subscribe('main_canvas.updated', self._on_canvas_changed)
        subscribe('main_canvas.resized', self._on_canvas_changed)
        
        # События проекта
        subscribe('project.settings_changed', self._on_project_settings_changed)
    
    def set_managers(self, element_manager, main_canvas):
        """Устанавливает менеджеры"""
        self.element_manager = element_manager
        self.main_canvas = main_canvas
        
        # Обновляем генератор кода
        if element_manager and main_canvas:
            elements = element_manager.get_all_elements()
            self.code_generator.set_elements(elements, main_canvas)
            self._invalidate_cache()
    
    def set_project_directory(self, directory: str):
        """Устанавливает папку проекта"""
        self.project_dir = Path(directory)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Папка проекта установлена: {directory}")
    
    def enable_auto_generation(self, enabled: bool = True):
        """Включает/выключает автоматическую генерацию"""
        self.auto_generation = enabled
        if enabled:
            self._regenerate_if_needed()
        log.info(f"Автогенерация {'включена' if enabled else 'отключена'}")
    
    def _on_element_changed(self, event_data=None):
        """Обработчик изменения элементов"""
        if not self.auto_generation:
            return
        
        # Обновляем список элементов в генераторе
        if self.element_manager:
            elements = self.element_manager.get_all_elements()
            self.code_generator.set_elements(elements, self.main_canvas)
        
        self._invalidate_cache()
        self._regenerate_if_needed()
        
        # Уведомляем об изменении проекта
        event_bus.emit('project.code_updated', {
            'html_updated': True,
            'css_updated': True, 
            'js_updated': True
        })
    
    def _on_canvas_changed(self, event_data=None):
        """Обработчик изменения главной панели"""
        if not self.auto_generation:
            return
        
        self._invalidate_cache()
        self._regenerate_if_needed()
        
        event_bus.emit('project.code_updated', {
            'html_updated': True,
            'css_updated': True
        })
    
    def _on_project_settings_changed(self, event_data=None):
        """Обработчик изменения настроек проекта"""
        self._invalidate_cache()
        if event_data and event_data.get('regenerate', True):
            self._regenerate_if_needed()
    
    def _invalidate_cache(self):
        """Сбрасывает кеш кода"""
        self._cache_valid = False
    
    def _regenerate_if_needed(self):
        """Генерирует код если кеш невалидный"""
        if not self._cache_valid:
            self._regenerate_code()
    
    def _regenerate_code(self):
        """Регенерирует весь код"""
        try:
            self._cached_html = self.code_generator.generate_html()
            self._cached_css = self.code_generator.generate_css() 
            self._cached_js = self.code_generator.generate_js()
            self._cache_valid = True
            
            # Автосохранение в проект папку
            if self.project_dir:
                self._auto_save_to_project()
                
            log.debug("Код регенерирован")
            
        except Exception as e:
            log.error(f"Ошибка генерации кода: {e}")
            self._cache_valid = False
    
    def _auto_save_to_project(self):
        """Автоматически сохраняет код в папку проекта"""
        try:
            # Сохраняем в базовом HTML формате
            html_file = self.project_dir / "index.html"
            css_file = self.project_dir / "style.css"
            js_file = self.project_dir / "script.js"
            
            # Создаём полный HTML документ
            full_html = self.code_generator.generate_all()
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(self._cached_css)
                
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(self._cached_js)
                
            log.debug(f"Автосохранение в {self.project_dir}")
            
        except Exception as e:
            log.error(f"Ошибка автосохранения: {e}")
    
    def get_generated_html(self) -> str:
        """Возвращает сгенерированный HTML"""
        self._regenerate_if_needed()
        return self._cached_html
    
    def get_generated_css(self) -> str:
        """Возвращает сгенерированный CSS"""
        self._regenerate_if_needed()
        return self._cached_css
    
    def get_generated_js(self) -> str:
        """Возвращает сгенерированный JavaScript"""
        self._regenerate_if_needed()
        return self._cached_js
    
    def get_full_html(self) -> str:
        """Возвращает полный HTML документ"""
        return self.code_generator.generate_all()
    
    def export_project(self, export_dir: str, template_name: str = 'html') -> str:
        """
        Экспортирует проект в указанную папку.
        
        Args:
            export_dir: Папка для экспорта
            template_name: Имя шаблона проекта
            
        Returns:
            Путь к экспортированному проекту
        """
        if template_name not in self.templates:
            raise ValueError(f"Неизвестный шаблон: {template_name}")
        
        template = self.templates[template_name]
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Генерируем актуальный код
        self._regenerate_if_needed()
        
        try:
            # Создаём файлы по шаблону
            for file_path, content in template.files.items():
                full_path = export_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Заменяем placeholder-ы реальным кодом
                if content == "<!-- Will be generated -->":
                    if template_name == 'html':
                        content = self.get_full_html()
                    elif template_name == 'react':
                        content = self.code_generator.export_react_component()
                    elif template_name == 'vue':
                        content = self.code_generator.export_vue_component()
                    else:
                        content = self._cached_html
                        
                elif content == "/* Will be generated */":
                    content = self._cached_css
                    
                elif content == "// Will be generated":
                    content = self._cached_js
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Создаём метаданные проекта
            meta = {
                'name': f"Generated Interface",
                'template': template_name,
                'generated_at': self._get_timestamp(),
                'elements_count': len(self.element_manager.get_all_elements()) if self.element_manager else 0,
                'canvas_size': {
                    'width': self.main_canvas.width if self.main_canvas else 0,
                    'height': self.main_canvas.height if self.main_canvas else 0
                }
            }
            
            with open(export_path / 'project.meta.json', 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            
            log.info(f"Проект экспортирован: {export_path}")
            return str(export_path)
            
        except Exception as e:
            log.error(f"Ошибка экспорта проекта: {e}")
            raise
    
    def create_zip_export(self, output_path: str, template_name: str = 'html') -> str:
        """
        Создаёт ZIP архив с проектом.
        
        Args:
            output_path: Путь к создаваемому ZIP файлу
            template_name: Имя шаблона проекта
            
        Returns:
            Путь к созданному ZIP файлу
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Экспортируем во временную папку
            temp_project = self.export_project(temp_dir, template_name)
            
            # Создаём ZIP архив
            zip_path = Path(output_path)
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.make_archive(
                str(zip_path.with_suffix('')), 
                'zip', 
                temp_project
            )
            
            final_path = str(zip_path.with_suffix('.zip'))
            log.info(f"ZIP архив создан: {final_path}")
            return final_path
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Возвращает статистику проекта"""
        stats = {
            'elements_count': 0,
            'lines_of_code': {
                'html': 0,
                'css': 0,
                'js': 0
            },
            'file_sizes': {
                'html': 0,
                'css': 0, 
                'js': 0
            },
            'canvas_size': {
                'width': 0,
                'height': 0
            },
            'auto_generation': self.auto_generation,
            'cache_valid': self._cache_valid
        }
        
        if self.element_manager:
            stats['elements_count'] = len(self.element_manager.get_all_elements())
        
        if self.main_canvas:
            stats['canvas_size']['width'] = self.main_canvas.width
            stats['canvas_size']['height'] = self.main_canvas.height
        
        # Подсчитываем строки и размеры
        self._regenerate_if_needed()
        
        stats['lines_of_code']['html'] = len(self._cached_html.splitlines())
        stats['lines_of_code']['css'] = len(self._cached_css.splitlines())
        stats['lines_of_code']['js'] = len(self._cached_js.splitlines())
        
        stats['file_sizes']['html'] = len(self._cached_html.encode('utf-8'))
        stats['file_sizes']['css'] = len(self._cached_css.encode('utf-8'))
        stats['file_sizes']['js'] = len(self._cached_js.encode('utf-8'))
        
        return stats
    
    def _get_timestamp(self) -> str:
        """Возвращает текущую временную метку"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # === Шаблоны файлов ===
    
    def _get_readme_template(self, framework: str = "HTML") -> str:
        """Шаблон README файла"""
        return f"""# Generated {framework} Interface

Этот интерфейс был автоматически сгенерирован из визуального редактора.

## Запуск

### {framework}
```bash
# Откройте index.html в браузере
open index.html
```

## Структура проекта

- `index.html` - Главная страница
- `style.css` - Стили интерфейса  
- `script.js` - JavaScript логика

## Разработка

Сгенерировано: {self._get_timestamp()}
"""

    def _get_package_json_template(self) -> str:
        """Шаблон package.json для HTML проекта"""
        return """{
  "name": "generated-interface",
  "version": "1.0.0",
  "description": "Generated HTML interface",
  "main": "index.html",
  "scripts": {
    "start": "python -m http.server 8000",
    "serve": "python -m http.server 8000"
  },
  "devDependencies": {
    "http-server": "^14.1.1"
  }
}"""

    def _get_react_index_template(self) -> str:
        """Шаблон index.js для React"""
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""

    def _get_react_html_template(self) -> str:
        """Шаблон index.html для React"""
        return """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Generated React Interface</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>"""

    def _get_react_package_template(self) -> str:
        """Шаблон package.json для React"""
        return """{
  "name": "generated-react-interface",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "devDependencies": {
    "react-scripts": "^5.0.1"
  }
}"""

    def _get_vue_main_template(self) -> str:
        """Шаблон main.js для Vue"""
        return """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')"""

    def _get_vue_html_template(self) -> str:
        """Шаблон index.html для Vue"""
        return """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated Vue Interface</title>
</head>
<body>
  <div id="app"></div>
</body>
</html>"""

    def _get_vue_package_template(self) -> str:
        """Шаблон package.json для Vue"""
        return """{
  "name": "generated-vue-interface",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "vue": "^3.3.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.0.0",
    "vite": "^4.0.0"
  }
}"""


# Глобальный экземпляр
_live_project_manager = None

def get_live_project_manager(config=None):
    """Получить глобальный экземпляр LiveProjectManager"""
    global _live_project_manager
    if _live_project_manager is None and config:
        _live_project_manager = LiveProjectManager(config)
    return _live_project_manager
