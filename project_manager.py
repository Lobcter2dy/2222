#!/usr/bin/env python3
"""
Менеджер проектов
Управление созданием, сохранением и загрузкой проектов
"""
import os
import json
import shutil
from datetime import datetime


class ProjectManager:
    """Менеджер проектов"""
    
    # Папка для проектов (рядом с приложением)
    PROJECTS_DIR = "projects"
    PROJECT_FILE = "project.json"
    THUMBNAIL_FILE = "thumbnail.png"
    
    def __init__(self, app_ref=None):
        self.app = app_ref
        self.current_project = None
        self.current_project_path = None
        
        # Создаём папку проектов если нет
        self._ensure_projects_dir()
    
    def _ensure_projects_dir(self):
        """Создаёт папку проектов если её нет"""
        if not os.path.exists(self.PROJECTS_DIR):
            os.makedirs(self.PROJECTS_DIR)
    
    def _get_project_path(self, project_name):
        """Возвращает путь к папке проекта"""
        # Очищаем имя от недопустимых символов
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return os.path.join(self.PROJECTS_DIR, safe_name)
    
    def _generate_unique_name(self, base_name="Новый проект"):
        """Генерирует уникальное имя проекта"""
        name = base_name
        counter = 1
        while os.path.exists(self._get_project_path(name)):
            name = f"{base_name} {counter}"
            counter += 1
        return name
    
    def get_all_projects(self):
        """Возвращает список всех проектов"""
        self._ensure_projects_dir()
        projects = []
        
        for folder in os.listdir(self.PROJECTS_DIR):
            project_path = os.path.join(self.PROJECTS_DIR, folder)
            project_file = os.path.join(project_path, self.PROJECT_FILE)
            
            if os.path.isdir(project_path) and os.path.exists(project_file):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        projects.append({
                            'name': data.get('name', folder),
                            'path': project_path,
                            'created': data.get('created', ''),
                            'modified': data.get('modified', ''),
                            'description': data.get('description', ''),
                        })
                except (json.JSONDecodeError, IOError, KeyError) as e:
                    # Если файл повреждён, всё равно показываем проект
                    print(f"[ProjectManager] Ошибка чтения {project_file}: {e}")
                    projects.append({
                        'name': folder,
                        'path': project_path,
                        'created': '',
                        'modified': '',
                        'description': '',
                    })
        
        # Сортируем по дате изменения (новые первые)
        projects.sort(key=lambda p: p.get('modified', ''), reverse=True)
        return projects
    
    def create_project(self, name, description=""):
        """Создаёт новый проект"""
        # Генерируем уникальное имя если нужно
        if not name:
            name = self._generate_unique_name()
        elif os.path.exists(self._get_project_path(name)):
            name = self._generate_unique_name(name)
        
        project_path = self._get_project_path(name)
        os.makedirs(project_path, exist_ok=True)
        
        # Создаём файл проекта
        now = datetime.now().isoformat()
        project_data = {
            'name': name,
            'description': description,
            'created': now,
            'modified': now,
            'version': '1.0',
            'canvas': {
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'fill_color': '#000000',
            },
            'elements': [],
            'mechanisms': [],
        }
        
        project_file = os.path.join(project_path, self.PROJECT_FILE)
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        self.current_project = name
        self.current_project_path = project_path
        
        return {
            'name': name,
            'path': project_path,
            'data': project_data
        }
    
    def save_project(self, name=None):
        """Сохраняет текущий проект"""
        if not self.app:
            return False
        
        # Если имя не указано, используем текущий проект
        if not name and self.current_project:
            name = self.current_project
        
        if not name:
            return False
        
        project_path = self._get_project_path(name)
        if not os.path.exists(project_path):
            os.makedirs(project_path, exist_ok=True)
        
        # Собираем данные проекта
        now = datetime.now().isoformat()
        
        # Данные главной панели
        canvas_data = {
            'width': self.app.main_canvas.width,
            'height': self.app.main_canvas.height,
            'x': self.app.main_canvas.x,
            'y': self.app.main_canvas.y,
            'fill_color': self.app.main_canvas.properties['fill_color'],
        }
        
        # Данные элементов
        elements_data = []
        for element in self.app.element_manager.get_all_elements():
            elements_data.append(element.to_dict())
        
        # Данные механизмов
        mechanisms_data = self.app.mechanism_manager.to_dict()
        
        # Загружаем существующие данные для сохранения created
        project_file = os.path.join(project_path, self.PROJECT_FILE)
        created = now
        description = ""
        if os.path.exists(project_file):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    created = old_data.get('created', now)
                    description = old_data.get('description', '')
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ProjectManager] Ошибка чтения старых данных: {e}")
        
        project_data = {
            'name': name,
            'description': description,
            'created': created,
            'modified': now,
            'version': '1.0',
            'canvas': canvas_data,
            'elements': elements_data,
            'mechanisms': mechanisms_data,
        }
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        self.current_project = name
        self.current_project_path = project_path
        
        print(f"[ProjectManager] Проект сохранён: {name}")
        return True
    
    def load_project(self, name):
        """Загружает проект"""
        if not self.app:
            return None
        
        project_path = self._get_project_path(name)
        project_file = os.path.join(project_path, self.PROJECT_FILE)
        
        if not os.path.exists(project_file):
            print(f"[ProjectManager] Проект не найден: {name}")
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ProjectManager] Ошибка загрузки: {e}")
            return None
        
        # Очищаем текущее состояние
        self.app.element_manager.clear_all()
        self.app.selection_tool.deselect()
        
        # Загружаем главную панель
        canvas_data = data.get('canvas', {})
        self.app.main_canvas.width = canvas_data.get('width', 1920)
        self.app.main_canvas.height = canvas_data.get('height', 1080)
        self.app.main_canvas.x = canvas_data.get('x', 0)
        self.app.main_canvas.y = canvas_data.get('y', 0)
        self.app.main_canvas.properties['fill_color'] = canvas_data.get('fill_color', '#000000')
        self.app.main_canvas.update()
        
        # Загружаем элементы
        elements_data = data.get('elements', [])
        for elem_data in elements_data:
            elem_type = elem_data.get('type')
            if elem_type:
                element = self.app.element_manager.create_element(
                    elem_type,
                    elem_data.get('x', 0),
                    elem_data.get('y', 0),
                    elem_data.get('width', 100),
                    elem_data.get('height', 100)
                )
                if element:
                    element.from_dict(elem_data)
                    element.update()
        
        # Загружаем механизмы
        mechanisms_data = data.get('mechanisms', [])
        self.app.mechanism_manager.from_dict(mechanisms_data)
        
        # Обновляем UI
        self.app._update_size_fields()
        self.app._update_grids()
        
        self.current_project = name
        self.current_project_path = project_path
        
        print(f"[ProjectManager] Проект загружен: {name}")
        return data
    
    def rename_project(self, old_name, new_name):
        """Переименовывает проект"""
        old_path = self._get_project_path(old_name)
        new_path = self._get_project_path(new_name)
        
        if not os.path.exists(old_path):
            return False
        
        if os.path.exists(new_path):
            return False
        
        try:
            # Переименовываем папку
            os.rename(old_path, new_path)
            
            # Обновляем имя в файле проекта
            project_file = os.path.join(new_path, self.PROJECT_FILE)
            if os.path.exists(project_file):
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['name'] = new_name
                data['modified'] = datetime.now().isoformat()
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Обновляем текущий проект если это он
            if self.current_project == old_name:
                self.current_project = new_name
                self.current_project_path = new_path
            
            print(f"[ProjectManager] Проект переименован: {old_name} → {new_name}")
            return True
        except Exception as e:
            print(f"[ProjectManager] Ошибка переименования: {e}")
            return False
    
    def delete_project(self, name):
        """Удаляет проект"""
        project_path = self._get_project_path(name)
        
        if not os.path.exists(project_path):
            return False
        
        try:
            shutil.rmtree(project_path)
            
            # Если удаляем текущий проект
            if self.current_project == name:
                self.current_project = None
                self.current_project_path = None
            
            print(f"[ProjectManager] Проект удалён: {name}")
            return True
        except Exception as e:
            print(f"[ProjectManager] Ошибка удаления: {e}")
            return False
    
    def update_description(self, name, description):
        """Обновляет описание проекта"""
        project_path = self._get_project_path(name)
        project_file = os.path.join(project_path, self.PROJECT_FILE)
        
        if not os.path.exists(project_file):
            return False
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['description'] = description
            data['modified'] = datetime.now().isoformat()
            
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"[ProjectManager] Ошибка обновления проекта: {e}")
            return False

