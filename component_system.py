#!/usr/bin/env python3
"""
Система компонентов (Component System)
Объединение элементов и механизмов в переиспользуемые группы
"""
import uuid
import json
import os
from datetime import datetime


class Component:
    """Компонент - группа элементов и механизмов"""
    
    def __init__(self, name="Компонент"):
        self.id = f"comp_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()
        
        # Содержимое
        self.elements = []      # Список словарей элементов
        self.mechanisms = []    # Список словарей механизмов
        
        # Метаданные
        self.tags = []
        self.category = "Пользовательские"
        self.icon = "📦"
        
        # Размеры группы (bounding box)
        self.width = 0
        self.height = 0
        self.origin_x = 0  # Относительная точка привязки
        self.origin_y = 0

    def add_element(self, element_data: dict):
        """Добавляет элемент в компонент"""
        self.elements.append(element_data)
        self._update_bounds()
        self.modified_at = datetime.now().isoformat()

    def add_mechanism(self, mechanism_data: dict):
        """Добавляет механизм в компонент"""
        self.mechanisms.append(mechanism_data)
        self.modified_at = datetime.now().isoformat()

    def _update_bounds(self):
        """Обновляет границы компонента"""
        if not self.elements:
            return
        
        min_x = min(e.get('x', 0) for e in self.elements)
        min_y = min(e.get('y', 0) for e in self.elements)
        max_x = max(e.get('x', 0) + e.get('width', 0) for e in self.elements)
        max_y = max(e.get('y', 0) + e.get('height', 0) for e in self.elements)
        
        self.origin_x = min_x
        self.origin_y = min_y
        self.width = max_x - min_x
        self.height = max_y - min_y

    def normalize_positions(self):
        """Нормализует позиции элементов относительно origin"""
        if not self.elements:
            return
        
        # Находим минимальные координаты
        min_x = min(e.get('x', 0) for e in self.elements)
        min_y = min(e.get('y', 0) for e in self.elements)
        
        # Сдвигаем все элементы
        for elem in self.elements:
            elem['x'] = elem.get('x', 0) - min_x
            elem['y'] = elem.get('y', 0) - min_y
        
        # Сдвигаем механизмы
        for mech in self.mechanisms:
            mech['x'] = mech.get('x', 0) - min_x
            mech['y'] = mech.get('y', 0) - min_y
        
        self._update_bounds()

    def to_dict(self) -> dict:
        """Сериализует компонент"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'elements': self.elements,
            'mechanisms': self.mechanisms,
            'tags': self.tags,
            'category': self.category,
            'icon': self.icon,
            'width': self.width,
            'height': self.height,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Component':
        """Десериализует компонент"""
        comp = cls(data.get('name', 'Компонент'))
        comp.id = data.get('id', comp.id)
        comp.description = data.get('description', '')
        comp.created_at = data.get('created_at', comp.created_at)
        comp.modified_at = data.get('modified_at', comp.modified_at)
        comp.elements = data.get('elements', [])
        comp.mechanisms = data.get('mechanisms', [])
        comp.tags = data.get('tags', [])
        comp.category = data.get('category', 'Пользовательские')
        comp.icon = data.get('icon', '📦')
        comp.width = data.get('width', 0)
        comp.height = data.get('height', 0)
        comp.origin_x = data.get('origin_x', 0)
        comp.origin_y = data.get('origin_y', 0)
        return comp


class ComponentManager:
    """Менеджер компонентов - объединение и размещение"""
    
    def __init__(self, element_manager, mechanism_manager, config):
        self.element_manager = element_manager
        self.mechanism_manager = mechanism_manager
        self.config = config
        
        # Текущий выбор для группировки
        self.selected_elements = []
        self.selected_mechanisms = []

    def create_component_from_selection(self, name="Новый компонент") -> Component:
        """Создаёт компонент из выбранных элементов"""
        component = Component(name)
        
        # Собираем выбранные элементы
        selected_elem = self.element_manager.selected_element
        if selected_elem:
            self.selected_elements = [selected_elem]
        
        # Добавляем элементы
        for elem in self.selected_elements:
            elem_data = elem.to_dict()
            component.add_element(elem_data)
        
        # Добавляем механизмы (если выбраны)
        selected_mech = self.mechanism_manager.selected_mechanism if self.mechanism_manager else None
        if selected_mech:
            self.selected_mechanisms = [selected_mech]
        
        for mech in self.selected_mechanisms:
            mech_data = mech.to_dict()
            component.add_mechanism(mech_data)
        
        # Нормализуем позиции
        component.normalize_positions()
        
        return component

    def create_component_from_elements(self, element_ids: list, mechanism_ids: list = None, name="Компонент") -> Component:
        """Создаёт компонент из списка ID элементов и механизмов"""
        component = Component(name)
        
        # Добавляем элементы по ID
        for elem_id in element_ids:
            elem = self.element_manager.get_element_by_id(elem_id)
            if elem:
                component.add_element(elem.to_dict())
        
        # Добавляем механизмы по ID
        if mechanism_ids and self.mechanism_manager:
            for mech_id in mechanism_ids:
                mech = self.mechanism_manager.get_mechanism_by_id(mech_id)
                if mech:
                    component.add_mechanism(mech.to_dict())
        
        component.normalize_positions()
        return component

    def place_component(self, component: Component, x: float, y: float) -> dict:
        """Размещает компонент на холсте в указанной позиции"""
        placed = {
            'elements': [],
            'mechanisms': []
        }
        
        # ID mapping (старый -> новый)
        id_mapping = {}
        
        # Размещаем элементы
        for elem_data in component.elements:
            # Создаём копию данных
            new_data = elem_data.copy()
            
            # Смещаем позицию
            new_data['x'] = elem_data.get('x', 0) + x
            new_data['y'] = elem_data.get('y', 0) + y
            
            # Создаём новый ID
            old_id = new_data.get('id', '')
            new_id = f"{old_id}_{uuid.uuid4().hex[:4]}"
            new_data['id'] = new_id
            id_mapping[old_id] = new_id
            
            # Создаём элемент
            elem_type = new_data.get('type', 'panel')
            new_elem = self.element_manager.create_element(
                elem_type,
                new_data['x'],
                new_data['y'],
                new_data.get('width', 100),
                new_data.get('height', 100)
            )
            
            if new_elem:
                # Применяем свойства
                new_elem.from_dict(new_data)
                new_elem.id = new_id
                new_elem.update()
                placed['elements'].append(new_elem)
        
        # Размещаем механизмы
        for mech_data in component.mechanisms:
            new_data = mech_data.copy()
            
            # Смещаем позицию
            new_data['x'] = mech_data.get('x', 0) + x
            new_data['y'] = mech_data.get('y', 0) + y
            
            # Новый ID
            old_id = new_data.get('id', '')
            new_id = f"{old_id}_{uuid.uuid4().hex[:4]}"
            new_data['id'] = new_id
            
            # Обновляем привязки элементов
            old_attached = new_data.get('attached_elements', [])
            new_attached = [id_mapping.get(eid, eid) for eid in old_attached]
            new_data['attached_elements'] = new_attached
            
            # Создаём механизм
            if self.mechanism_manager:
                mech_type = new_data.get('type', 'move_track')
                new_mech = self.mechanism_manager.create_mechanism(
                    mech_type,
                    new_data['x'],
                    new_data['y'],
                    new_data.get('width', 100),
                    new_data.get('height', 20)
                )
                
                if new_mech:
                    new_mech.from_dict(new_data)
                    new_mech.id = new_id
                    new_mech.update()
                    placed['mechanisms'].append(new_mech)
        
        return placed

    def set_selected_elements(self, elements: list):
        """Устанавливает выбранные элементы"""
        self.selected_elements = elements

    def set_selected_mechanisms(self, mechanisms: list):
        """Устанавливает выбранные механизмы"""
        self.selected_mechanisms = mechanisms


class ArtifactManager:
    """Менеджер артефактов - сохранение и загрузка заготовок"""
    
    ARTIFACTS_DIR = "artifacts"
    ARTIFACTS_FILE = "artifacts.json"
    
    # Встроенные категории
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

    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.artifacts_path = os.path.join(self.project_path, self.ARTIFACTS_DIR)
        self.artifacts_file = os.path.join(self.artifacts_path, self.ARTIFACTS_FILE)
        
        # Список артефактов
        self.artifacts = []  # List[Component]
        
        # Загружаем существующие
        self._ensure_directory()
        self.load_artifacts()

    def _ensure_directory(self):
        """Создаёт директорию артефактов если нет"""
        if not os.path.exists(self.artifacts_path):
            os.makedirs(self.artifacts_path)

    def save_artifact(self, component: Component) -> bool:
        """Сохраняет компонент как артефакт"""
        try:
            # Проверяем уникальность имени
            existing_names = [a.name for a in self.artifacts]
            if component.name in existing_names:
                # Добавляем суффикс
                i = 1
                base_name = component.name
                while f"{base_name} ({i})" in existing_names:
                    i += 1
                component.name = f"{base_name} ({i})"
            
            self.artifacts.append(component)
            self._save_to_file()
            return True
        except Exception as e:
            print(f"[ArtifactManager] Ошибка сохранения: {e}")
            return False

    def delete_artifact(self, artifact_id: str) -> bool:
        """Удаляет артефакт"""
        for i, artifact in enumerate(self.artifacts):
            if artifact.id == artifact_id:
                self.artifacts.pop(i)
                self._save_to_file()
                return True
        return False

    def get_artifact(self, artifact_id: str) -> Component:
        """Возвращает артефакт по ID"""
        for artifact in self.artifacts:
            if artifact.id == artifact_id:
                return artifact
        return None

    def get_artifact_by_name(self, name: str) -> Component:
        """Возвращает артефакт по имени"""
        for artifact in self.artifacts:
            if artifact.name == name:
                return artifact
        return None

    def get_artifacts_by_category(self, category: str) -> list:
        """Возвращает артефакты категории"""
        return [a for a in self.artifacts if a.category == category]

    def get_all_artifacts(self) -> list:
        """Возвращает все артефакты"""
        return self.artifacts.copy()

    def update_artifact(self, artifact_id: str, updates: dict) -> bool:
        """Обновляет артефакт"""
        for artifact in self.artifacts:
            if artifact.id == artifact_id:
                if 'name' in updates:
                    artifact.name = updates['name']
                if 'description' in updates:
                    artifact.description = updates['description']
                if 'category' in updates:
                    artifact.category = updates['category']
                if 'tags' in updates:
                    artifact.tags = updates['tags']
                if 'icon' in updates:
                    artifact.icon = updates['icon']
                artifact.modified_at = datetime.now().isoformat()
                self._save_to_file()
                return True
        return False

    def _save_to_file(self):
        """Сохраняет артефакты в файл"""
        data = {
            'version': '1.0',
            'artifacts': [a.to_dict() for a in self.artifacts]
        }
        
        with open(self.artifacts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_artifacts(self):
        """Загружает артефакты из файла"""
        if not os.path.exists(self.artifacts_file):
            self.artifacts = []
            return
        
        try:
            with open(self.artifacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.artifacts = []
            for artifact_data in data.get('artifacts', []):
                artifact = Component.from_dict(artifact_data)
                self.artifacts.append(artifact)
        except Exception as e:
            print(f"[ArtifactManager] Ошибка загрузки: {e}")
            self.artifacts = []

    def export_artifact(self, artifact_id: str, filepath: str) -> bool:
        """Экспортирует артефакт в отдельный файл"""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(artifact.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[ArtifactManager] Ошибка экспорта: {e}")
            return False

    def import_artifact(self, filepath: str) -> Component:
        """Импортирует артефакт из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            artifact = Component.from_dict(data)
            self.save_artifact(artifact)
            return artifact
        except Exception as e:
            print(f"[ArtifactManager] Ошибка импорта: {e}")
            return None

    def search_artifacts(self, query: str) -> list:
        """Поиск артефактов по имени, описанию, тегам"""
        query = query.lower()
        results = []
        
        for artifact in self.artifacts:
            if query in artifact.name.lower():
                results.append(artifact)
            elif query in artifact.description.lower():
                results.append(artifact)
            elif any(query in tag.lower() for tag in artifact.tags):
                results.append(artifact)
        
        return results

