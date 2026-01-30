"""
Модуль для интеграции с мессенджером MAX
Отправка кодов подтверждения при шифровании и дешифровании данных
"""

import requests
import json
import secrets
import string
from typing import Optional, Tuple
from datetime import datetime


class MaxMessenger:
    """Класс для работы с мессенджером MAX"""
    
    def __init__(self, api_key: str = "", chat_id: str = "", phone_number: str = ""):
        """
        Инициализация мессенджера MAX
        
        Args:
            api_key: API ключ для доступа к мессенджеру
            chat_id: ID чата или получателя
            phone_number: Номер телефона получателя
        """
        self.api_key = api_key
        self.chat_id = chat_id
        self.phone_number = phone_number
        # Базовый URL API мессенджера MAX (может потребоваться настройка)
        self.api_base_url = "https://api.max.im/v1"  # Примерный URL, нужно уточнить
        self.enabled = bool(api_key and (chat_id or phone_number))
    
    def generate_verification_code(self, length: int = 6) -> str:
        """
        Генерация кода подтверждения
        
        Args:
            length: Длина кода
            
        Returns:
            Сгенерированный код
        """
        characters = string.digits
        code = ''.join(secrets.choice(characters) for _ in range(length))
        return code
    
    def send_message(self, message: str, recipient: Optional[str] = None) -> Tuple[bool, str]:
        """
        Отправка сообщения через мессенджер MAX
        
        Args:
            message: Текст сообщения
            recipient: Получатель (если не указан, используется chat_id или phone_number)
            
        Returns:
            Кортеж (успех, сообщение об ошибке)
        """
        if not self.enabled:
            return False, "Мессенджер не настроен"
        
        try:
            recipient = recipient or self.chat_id or self.phone_number
            
            # Вариант 1: Отправка через API мессенджера MAX
            # Нужно уточнить точный формат API для мессенджера MAX
            payload = {
                "api_key": self.api_key,
                "recipient": recipient,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Попытка отправки через API
            try:
                response = requests.post(
                    f"{self.api_base_url}/messages/send",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return True, "Сообщение отправлено"
                else:
                    return False, f"Ошибка API: {response.status_code}"
            except requests.exceptions.RequestException:
                # Если API недоступен, используем альтернативный метод
                # Можно использовать файловый лог или другой способ
                return self._send_alternative(message, recipient)
        
        except Exception as e:
            return False, f"Ошибка отправки: {str(e)}"
    
    def _send_alternative(self, message: str, recipient: str) -> Tuple[bool, str]:
        """
        Альтернативный метод отправки (если API недоступен)
        Сохраняет сообщения в файл для тестирования
        
        Args:
            message: Текст сообщения
            recipient: Получатель
            
        Returns:
            Кортеж (успех, сообщение)
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "recipient": recipient,
                "message": message
            }
            
            # Сохранение в файл для тестирования
            with open("max_messenger_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            return True, "Сообщение сохранено в лог (API недоступен)"
        except Exception as e:
            return False, f"Ошибка альтернативной отправки: {str(e)}"
    
    def send_encryption_code(self, code: str, data_type: str, record_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Отправка кода подтверждения при шифровании
        
        Args:
            code: Код подтверждения
            data_type: Тип данных (ученик, учитель, родитель)
            record_id: ID записи в базе данных
            
        Returns:
            Кортеж (успех, сообщение)
        """
        message = f"""
🔐 КОД ПОДТВЕРЖДЕНИЯ ШИФРОВАНИЯ

Тип данных: {data_type}
ID записи: {record_id if record_id else 'N/A'}
Код подтверждения: {code}

Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

⚠️ Сохраните этот код для подтверждения операции.
        """.strip()
        
        return self.send_message(message)
    
    def send_decryption_code(self, code: str, record_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Отправка кода подтверждения при дешифровании
        
        Args:
            code: Код подтверждения
            record_id: ID записи в базе данных
            
        Returns:
            Кортеж (успех, сообщение)
        """
        message = f"""
🔓 КОД ПОДТВЕРЖДЕНИЯ ДЕШИФРОВАНИЯ

ID записи: {record_id if record_id else 'N/A'}
Код подтверждения: {code}

Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

⚠️ Сохраните этот код для подтверждения операции.
        """.strip()
        
        return self.send_message(message)
    
    def send_operation_notification(self, operation: str, status: str, details: str = "") -> Tuple[bool, str]:
        """
        Отправка уведомления об операции
        
        Args:
            operation: Тип операции (шифрование/дешифрование)
            status: Статус (успех/ошибка)
            details: Дополнительные детали
            
        Returns:
            Кортеж (успех, сообщение)
        """
        emoji = "✅" if status == "успех" else "❌"
        message = f"""
{emoji} УВЕДОМЛЕНИЕ ОБ ОПЕРАЦИИ

Операция: {operation}
Статус: {status}
{details if details else ''}

Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """.strip()
        
        return self.send_message(message)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Тестирование подключения к мессенджеру
        
        Returns:
            Кортеж (успех, сообщение)
        """
        if not self.enabled:
            return False, "Мессенджер не настроен"
        
        test_message = "Тестовое сообщение от программы защиты персональных данных"
        return self.send_message(test_message)
    
    def save_config(self, config_file: str = "max_messenger_config.json"):
        """
        Сохранение конфигурации в файл
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        config = {
            "api_key": self.api_key,
            "chat_id": self.chat_id,
            "phone_number": self.phone_number,
            "enabled": self.enabled
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_config(cls, config_file: str = "max_messenger_config.json") -> 'MaxMessenger':
        """
        Загрузка конфигурации из файла
        
        Args:
            config_file: Путь к файлу конфигурации
            
        Returns:
            Экземпляр MaxMessenger с загруженной конфигурацией
        """
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            return cls(
                api_key=config.get("api_key", ""),
                chat_id=config.get("chat_id", ""),
                phone_number=config.get("phone_number", "")
            )
        except FileNotFoundError:
            return cls()
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return cls()


class CodeVerification:
    """Класс для управления кодами подтверждения"""
    
    def __init__(self):
        self.active_codes = {}  # {code: (operation, timestamp, record_id)}
        self.code_expiry_minutes = 10  # Время жизни кода в минутах
    
    def generate_and_store_code(self, operation: str, record_id: Optional[int] = None) -> str:
        """
        Генерация и сохранение кода подтверждения
        
        Args:
            operation: Тип операции (encrypt/decrypt)
            record_id: ID записи
            
        Returns:
            Сгенерированный код
        """
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.active_codes[code] = {
            "operation": operation,
            "timestamp": datetime.now(),
            "record_id": record_id
        }
        return code
    
    def verify_code(self, code: str, operation: str) -> Tuple[bool, str]:
        """
        Проверка кода подтверждения
        
        Args:
            code: Код для проверки
            operation: Ожидаемая операция
            
        Returns:
            Кортеж (валидность, сообщение)
        """
        if code not in self.active_codes:
            return False, "Код не найден или истек"
        
        code_data = self.active_codes[code]
        
        # Проверка времени жизни
        elapsed = (datetime.now() - code_data["timestamp"]).total_seconds() / 60
        if elapsed > self.code_expiry_minutes:
            del self.active_codes[code]
            return False, "Код истек"
        
        # Проверка операции
        if code_data["operation"] != operation:
            return False, "Код не соответствует операции"
        
        # Удаление использованного кода
        del self.active_codes[code]
        return True, "Код подтвержден"
    
    def cleanup_expired_codes(self):
        """Очистка истекших кодов"""
        current_time = datetime.now()
        expired_codes = [
            code for code, data in self.active_codes.items()
            if (current_time - data["timestamp"]).total_seconds() / 60 > self.code_expiry_minutes
        ]
        
        for code in expired_codes:
            del self.active_codes[code]
