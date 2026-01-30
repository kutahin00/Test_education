"""
Модуль шифрования персональных данных
Использует алгоритм AES-256 для защиты информации
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from datetime import datetime
from typing import Tuple


class PersonalDataEncryption:
    """Класс для шифрования и дешифрования персональных данных"""
    
    def __init__(self, password: str):
        """
        Инициализация с паролем пользователя
        
        Args:
            password: Пароль для генерации ключа шифрования
        """
        self.password = password.encode()
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)
    
    def _generate_key(self) -> bytes:
        """
        Генерация ключа шифрования из пароля
        
        Returns:
            Ключ шифрования в формате Fernet
        """
        # Используем соль для дополнительной безопасности
        salt = b'school_data_protection_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_data(self, data: dict) -> str:
        """
        Шифрование словаря с персональными данными
        
        Args:
            data: Словарь с персональными данными
            
        Returns:
            Зашифрованная строка в формате JSON
        """
        # Добавляем метаданные о времени шифрования
        data['_encrypted_at'] = datetime.now().isoformat()
        
        # Преобразуем в JSON и шифруем
        json_data = json.dumps(data, ensure_ascii=False)
        encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
        
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_string: str) -> dict:
        """
        Дешифрование строки с персональными данными
        
        Args:
            encrypted_string: Зашифрованная строка
            
        Returns:
            Словарь с персональными данными
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_string.encode('utf-8'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            json_data = decrypted_bytes.decode('utf-8')
            data = json.loads(json_data)
            
            # Удаляем служебные поля
            data.pop('_encrypted_at', None)
            
            return data
        except Exception as e:
            raise ValueError(f"Ошибка дешифрования: {str(e)}")
    
    def encrypt_file(self, input_file: str, output_file: str):
        """
        Шифрование файла
        
        Args:
            input_file: Путь к исходному файлу
            output_file: Путь к зашифрованному файлу
        """
        with open(input_file, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, input_file: str, output_file: str):
        """
        Дешифрование файла
        
        Args:
            input_file: Путь к зашифрованному файлу
            output_file: Путь к расшифрованному файлу
        """
        try:
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
        except Exception as e:
            raise ValueError(f"Ошибка дешифрования файла: {str(e)}")


class DataValidator:
    """Класс для валидации персональных данных"""
    
    @staticmethod
    def validate_student_data(data: dict) -> Tuple[bool, str]:
        """
        Валидация данных ученика
        
        Args:
            data: Словарь с данными ученика
            
        Returns:
            Кортеж (успех, сообщение об ошибке)
        """
        required_fields = ['фамилия', 'имя', 'отчество', 'дата_рождения', 'класс']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Отсутствует обязательное поле: {field}"
        
        # Проверка формата даты рождения
        try:
            datetime.strptime(data['дата_рождения'], '%d.%m.%Y')
        except ValueError:
            return False, "Неверный формат даты рождения. Используйте ДД.ММ.ГГГГ"
        
        return True, "Данные валидны"
    
    @staticmethod
    def validate_teacher_data(data: dict) -> Tuple[bool, str]:
        """
        Валидация данных учителя
        
        Args:
            data: Словарь с данными учителя
            
        Returns:
            Кортеж (успех, сообщение об ошибке)
        """
        required_fields = ['фамилия', 'имя', 'отчество', 'должность']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Отсутствует обязательное поле: {field}"
        
        return True, "Данные валидны"
