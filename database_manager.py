"""
Модуль для работы с базой данных зашифрованных персональных данных
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    """Класс для управления базой данных зашифрованных данных"""
    
    def __init__(self, db_file: str = "encrypted_database.json"):
        """
        Инициализация менеджера базы данных
        
        Args:
            db_file: Путь к файлу базы данных
        """
        self.db_file = db_file
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Создание файла базы данных, если он не существует"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({"records": []}, f, ensure_ascii=False, indent=2)
    
    def add_record(self, encrypted_data: str, record_type: str, description: str = ""):
        """
        Добавление записи в базу данных
        
        Args:
            encrypted_data: Зашифрованные данные
            record_type: Тип записи (ученик, учитель, родитель)
            description: Описание записи
        """
        with open(self.db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        record = {
            "id": len(db["records"]) + 1,
            "type": record_type,
            "description": description,
            "encrypted_data": encrypted_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        db["records"].append(record)
        
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        
        return record["id"]
    
    def get_all_records(self) -> List[Dict]:
        """
        Получение всех записей из базы данных
        
        Returns:
            Список записей (без расшифровки)
        """
        with open(self.db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        return db["records"]
    
    def get_record(self, record_id: int) -> Optional[Dict]:
        """
        Получение конкретной записи по ID
        
        Args:
            record_id: ID записи
            
        Returns:
            Запись или None, если не найдена
        """
        records = self.get_all_records()
        for record in records:
            if record["id"] == record_id:
                return record
        return None
    
    def delete_record(self, record_id: int) -> bool:
        """
        Удаление записи из базы данных
        
        Args:
            record_id: ID записи для удаления
            
        Returns:
            True, если запись удалена, False если не найдена
        """
        with open(self.db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        initial_count = len(db["records"])
        db["records"] = [r for r in db["records"] if r["id"] != record_id]
        
        if len(db["records"]) < initial_count:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            return True
        
        return False
    
    def update_record(self, record_id: int, encrypted_data: str, description: str = ""):
        """
        Обновление записи в базе данных
        
        Args:
            record_id: ID записи
            encrypted_data: Новые зашифрованные данные
            description: Новое описание
        """
        with open(self.db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        for record in db["records"]:
            if record["id"] == record_id:
                record["encrypted_data"] = encrypted_data
                record["description"] = description
                record["updated_at"] = datetime.now().isoformat()
                break
        
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """
        Получение статистики по базе данных
        
        Returns:
            Словарь со статистикой
        """
        records = self.get_all_records()
        
        stats = {
            "total_records": len(records),
            "by_type": {}
        }
        
        for record in records:
            record_type = record["type"]
            stats["by_type"][record_type] = stats["by_type"].get(record_type, 0) + 1
        
        return stats
