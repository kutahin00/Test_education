"""
Графический интерфейс для программы шифрования персональных данных
Дипломная работа: "Защита персональных данных в школе"
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from encryption_module import PersonalDataEncryption, DataValidator
from database_manager import DatabaseManager
from max_messenger import MaxMessenger, CodeVerification
import json
from datetime import datetime


class PersonalDataEncryptionApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Защита персональных данных в школе")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Инициализация компонентов
        self.encryption = None
        self.db_manager = DatabaseManager()
        self.max_messenger = MaxMessenger.load_config()
        self.code_verification = CodeVerification()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка статистики
        self.update_statistics()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Настройка пароля
        password_frame = ttk.Frame(notebook)
        notebook.add(password_frame, text="Настройка пароля")
        self.create_password_tab(password_frame)
        
        # Вкладка 2: Шифрование данных
        encrypt_frame = ttk.Frame(notebook)
        notebook.add(encrypt_frame, text="Шифрование данных")
        self.create_encrypt_tab(encrypt_frame)
        
        # Вкладка 3: Дешифрование данных
        decrypt_frame = ttk.Frame(notebook)
        notebook.add(decrypt_frame, text="Дешифрование данных")
        self.create_decrypt_tab(decrypt_frame)
        
        # Вкладка 4: База данных
        database_frame = ttk.Frame(notebook)
        notebook.add(database_frame, text="База данных")
        self.create_database_tab(database_frame)
        
        # Вкладка 5: Настройка мессенджера MAX
        messenger_frame = ttk.Frame(notebook)
        notebook.add(messenger_frame, text="Мессенджер MAX")
        self.create_messenger_tab(messenger_frame)
        
        # Вкладка 6: О программе
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="О программе")
        self.create_about_tab(about_frame)
    
    def create_password_tab(self, parent):
        """Создание вкладки настройки пароля"""
        frame = ttk.LabelFrame(parent, text="Настройка пароля шифрования", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Введите пароль для шифрования данных:", font=("Arial", 10)).pack(pady=5)
        
        self.password_entry = ttk.Entry(frame, show="*", width=40, font=("Arial", 10))
        self.password_entry.pack(pady=5)
        
        ttk.Label(frame, text="Подтвердите пароль:", font=("Arial", 10)).pack(pady=5)
        
        self.password_confirm_entry = ttk.Entry(frame, show="*", width=40, font=("Arial", 10))
        self.password_confirm_entry.pack(pady=5)
        
        ttk.Button(frame, text="Установить пароль", command=self.set_password).pack(pady=20)
        
        self.password_status_label = ttk.Label(frame, text="Пароль не установлен", 
                                               foreground="red", font=("Arial", 9))
        self.password_status_label.pack(pady=5)
    
    def create_encrypt_tab(self, parent):
        """Создание вкладки шифрования"""
        # Выбор типа данных
        type_frame = ttk.LabelFrame(parent, text="Тип данных", padding=10)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.data_type_var = tk.StringVar(value="ученик")
        ttk.Radiobutton(type_frame, text="Ученик", variable=self.data_type_var, 
                       value="ученик").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Учитель", variable=self.data_type_var, 
                       value="учитель").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Родитель", variable=self.data_type_var, 
                       value="родитель").pack(side=tk.LEFT, padx=10)
        
        # Поля для ввода данных
        data_frame = ttk.LabelFrame(parent, text="Персональные данные", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.data_fields = {}
        
        # Поля для ученика
        student_fields = [
            ("фамилия", "Фамилия:"),
            ("имя", "Имя:"),
            ("отчество", "Отчество:"),
            ("дата_рождения", "Дата рождения (ДД.ММ.ГГГГ):"),
            ("класс", "Класс:"),
            ("адрес", "Адрес:"),
            ("телефон", "Телефон:"),
            ("email", "Email:"),
            ("медицинская_информация", "Медицинская информация:")
        ]
        
        # Поля для учителя
        teacher_fields = [
            ("фамилия", "Фамилия:"),
            ("имя", "Имя:"),
            ("отчество", "Отчество:"),
            ("должность", "Должность:"),
            ("предмет", "Предмет:"),
            ("телефон", "Телефон:"),
            ("email", "Email:"),
            ("образование", "Образование:")
        ]
        
        # Создание полей
        for i, (field_name, field_label) in enumerate(student_fields):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(data_frame, text=field_label).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(data_frame, width=30)
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            self.data_fields[field_name] = entry
        
        # Поле для кода подтверждения
        code_frame = ttk.LabelFrame(parent, text="Код подтверждения из мессенджера MAX", padding=10)
        code_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(code_frame, text="Введите код подтверждения (если требуется):", 
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.encrypt_code_entry = ttk.Entry(code_frame, width=15, font=("Arial", 10))
        self.encrypt_code_entry.pack(side=tk.LEFT, padx=5)
        
        self.encrypt_code_status = ttk.Label(code_frame, text="", font=("Arial", 8))
        self.encrypt_code_status.pack(side=tk.LEFT, padx=5)
        
        # Кнопки действий
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Зашифровать и сохранить", 
                  command=self.encrypt_and_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить поля", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Загрузить из файла", 
                  command=self.load_from_file).pack(side=tk.LEFT, padx=5)
    
    def create_decrypt_tab(self, parent):
        """Создание вкладки дешифрования"""
        # Выбор записи из базы данных
        select_frame = ttk.LabelFrame(parent, text="Выбор записи", padding=10)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(select_frame, text="ID записи:").pack(side=tk.LEFT, padx=5)
        self.record_id_entry = ttk.Entry(select_frame, width=10)
        self.record_id_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(select_frame, text="Загрузить и расшифровать", 
                  command=self.decrypt_from_database).pack(side=tk.LEFT, padx=10)
        
        # Поле для кода подтверждения
        code_frame = ttk.LabelFrame(parent, text="Код подтверждения из мессенджера MAX", padding=10)
        code_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(code_frame, text="Введите код подтверждения (если требуется):", 
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.decrypt_code_entry = ttk.Entry(code_frame, width=15, font=("Arial", 10))
        self.decrypt_code_entry.pack(side=tk.LEFT, padx=5)
        
        self.decrypt_code_status = ttk.Label(code_frame, text="", font=("Arial", 8))
        self.decrypt_code_status.pack(side=tk.LEFT, padx=5)
        
        # Или ввод зашифрованных данных вручную
        manual_frame = ttk.LabelFrame(parent, text="Или введите зашифрованные данные вручную", padding=10)
        manual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.encrypted_data_text = scrolledtext.ScrolledText(manual_frame, height=5, width=80)
        self.encrypted_data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(manual_frame, text="Расшифровать", 
                  command=self.decrypt_manual).pack(pady=5)
        
        # Результат дешифрования
        result_frame = ttk.LabelFrame(parent, text="Результат дешифрования", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.decrypted_data_text = scrolledtext.ScrolledText(result_frame, height=10, width=80)
        self.decrypted_data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_database_tab(self, parent):
        """Создание вкладки базы данных"""
        # Статистика
        stats_frame = ttk.LabelFrame(parent, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack()
        
        # Список записей
        list_frame = ttk.LabelFrame(parent, text="Записи в базе данных", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица записей
        columns = ("ID", "Тип", "Описание", "Создано")
        self.records_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)
        
        self.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Обновить список", 
                  command=self.refresh_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить запись", 
                  command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в файл", 
                  command=self.export_database).pack(side=tk.LEFT, padx=5)
        
        # Загрузка записей при открытии
        self.refresh_database()
    
    def create_messenger_tab(self, parent):
        """Создание вкладки настройки мессенджера MAX"""
        # Настройки подключения
        config_frame = ttk.LabelFrame(parent, text="Настройки подключения", padding=20)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(config_frame, text="API ключ:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(config_frame, width=50, font=("Arial", 10))
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        if self.max_messenger.api_key:
            self.api_key_entry.insert(0, self.max_messenger.api_key)
        
        ttk.Label(config_frame, text="ID чата:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.chat_id_entry = ttk.Entry(config_frame, width=50, font=("Arial", 10))
        self.chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
        if self.max_messenger.chat_id:
            self.chat_id_entry.insert(0, self.max_messenger.chat_id)
        
        ttk.Label(config_frame, text="Номер телефона:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_entry = ttk.Entry(config_frame, width=50, font=("Arial", 10))
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)
        if self.max_messenger.phone_number:
            self.phone_entry.insert(0, self.max_messenger.phone_number)
        
        # Кнопки управления
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить настройки", 
                  command=self.save_messenger_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Тест подключения", 
                  command=self.test_messenger_connection).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.messenger_status_label = ttk.Label(config_frame, 
                                                text="Мессенджер не настроен" if not self.max_messenger.enabled else "Мессенджер настроен",
                                                foreground="red" if not self.max_messenger.enabled else "green",
                                                font=("Arial", 9))
        self.messenger_status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Информация
        info_frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = """
Мессенджер MAX используется для отправки кодов подтверждения при операциях шифрования и дешифрования.

Как это работает:
1. При шифровании данных генерируется код подтверждения
2. Код отправляется в мессенджер MAX
3. Пользователь вводит код для подтверждения операции
4. Операция выполняется только после подтверждения кода

Настройка:
- Укажите API ключ для доступа к мессенджеру MAX
- Укажите ID чата или номер телефона получателя
- Нажмите "Сохранить настройки"
- Проверьте подключение кнопкой "Тест подключения"

Примечание: Если API мессенджера недоступен, сообщения будут сохраняться в файл max_messenger_log.json
        """
        
        info_widget = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=10, font=("Arial", 9))
        info_widget.pack(fill=tk.BOTH, expand=True)
        info_widget.insert("1.0", info_text.strip())
        info_widget.config(state=tk.DISABLED)
    
    def save_messenger_config(self):
        """Сохранение настроек мессенджера"""
        api_key = self.api_key_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        self.max_messenger = MaxMessenger(api_key, chat_id, phone)
        self.max_messenger.save_config()
        
        if self.max_messenger.enabled:
            self.messenger_status_label.config(text="Мессенджер настроен", foreground="green")
            messagebox.showinfo("Успех", "Настройки мессенджера сохранены")
        else:
            self.messenger_status_label.config(text="Мессенджер не настроен", foreground="red")
            messagebox.showwarning("Предупреждение", "Укажите API ключ и получателя")
    
    def test_messenger_connection(self):
        """Тестирование подключения к мессенджеру"""
        if not self.max_messenger.enabled:
            messagebox.showerror("Ошибка", "Сначала настройте мессенджер")
            return
        
        success, message = self.max_messenger.test_connection()
        if success:
            messagebox.showinfo("Успех", f"Подключение успешно: {message}")
        else:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {message}")
    
    def create_about_tab(self, parent):
        """Создание вкладки о программе"""
        about_text = """
ПРОГРАММА ЗАЩИТЫ ПЕРСОНАЛЬНЫХ ДАННЫХ В ШКОЛЕ

Версия: 1.0
Дата разработки: 2024

ОПИСАНИЕ:
Программа предназначена для безопасного хранения и обработки 
персональных данных учащихся, учителей и родителей в образовательных 
учреждениях.

ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Шифрование персональных данных с использованием алгоритма AES-256
• Безопасное хранение данных в зашифрованном виде
• Управление базой данных зашифрованных записей
• Валидация вводимых данных
• Экспорт и импорт данных

ТЕХНОЛОГИИ:
• Python 3.x
• Библиотека cryptography (Fernet)
• Алгоритм шифрования: AES-256
• Формат ключа: PBKDF2 с SHA-256

БЕЗОПАСНОСТЬ:
• Все данные шифруются перед сохранением
• Пароль используется для генерации ключа шифрования
• Ключ никогда не хранится в открытом виде
• Используются современные криптографические стандарты

АВТОР:
Разработано для дипломной работы
"Защита персональных данных в школе"

ЛИЦЕНЗИЯ:
Для использования в образовательных целях
        """
        
        text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", about_text)
        text_widget.config(state=tk.DISABLED)
    
    def set_password(self):
        """Установка пароля для шифрования"""
        password = self.password_entry.get()
        password_confirm = self.password_confirm_entry.get()
        
        if not password:
            messagebox.showerror("Ошибка", "Введите пароль")
            return
        
        if password != password_confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        if len(password) < 8:
            messagebox.showwarning("Предупреждение", 
                                 "Рекомендуется использовать пароль длиной не менее 8 символов")
        
        try:
            self.encryption = PersonalDataEncryption(password)
            self.password_status_label.config(text="Пароль установлен", foreground="green")
            messagebox.showinfo("Успех", "Пароль успешно установлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при установке пароля: {str(e)}")
    
    def encrypt_and_save(self):
        """Шифрование данных и сохранение в базу"""
        if not self.encryption:
            messagebox.showerror("Ошибка", "Сначала установите пароль")
            return
        
        # Сбор данных из полей
        data = {}
        for field_name, entry in self.data_fields.items():
            value = entry.get().strip()
            if value:
                data[field_name] = value
        
        if not data:
            messagebox.showerror("Ошибка", "Введите хотя бы одно поле данных")
            return
        
        # Валидация данных
        data_type = self.data_type_var.get()
        if data_type == "ученик":
            is_valid, message = DataValidator.validate_student_data(data)
        elif data_type == "учитель":
            is_valid, message = DataValidator.validate_teacher_data(data)
        else:
            is_valid, message = True, "Данные валидны"
        
        if not is_valid:
            messagebox.showerror("Ошибка валидации", message)
            return
        
        try:
            # Генерация и отправка кода подтверждения
            verification_code = None
            if self.max_messenger.enabled:
                verification_code = self.code_verification.generate_and_store_code("encrypt")
                record_id = len(self.db_manager.get_all_records()) + 1
                success, msg = self.max_messenger.send_encryption_code(verification_code, data_type, record_id)
                
                if success:
                    # Запрос кода подтверждения
                    code_input = self.encrypt_code_entry.get().strip()
                    if not code_input:
                        # Показываем диалог для ввода кода
                        code_dialog = tk.Toplevel(self.root)
                        code_dialog.title("Код подтверждения")
                        code_dialog.geometry("400x150")
                        code_dialog.transient(self.root)
                        code_dialog.grab_set()
                        
                        ttk.Label(code_dialog, 
                                 text=f"Код отправлен в мессенджер MAX.\nВведите код подтверждения:",
                                 font=("Arial", 10)).pack(pady=10)
                        
                        code_entry = ttk.Entry(code_dialog, width=20, font=("Arial", 12))
                        code_entry.pack(pady=5)
                        code_entry.focus()
                        
                        result = {"code": None}
                        
                        def confirm_code():
                            result["code"] = code_entry.get().strip()
                            code_dialog.destroy()
                        
                        ttk.Button(code_dialog, text="Подтвердить", command=confirm_code).pack(pady=5)
                        code_dialog.bind('<Return>', lambda e: confirm_code())
                        
                        code_dialog.wait_window()
                        code_input = result["code"]
                    
                    # Проверка кода
                    is_valid, code_msg = self.code_verification.verify_code(code_input, "encrypt")
                    if not is_valid:
                        self.encrypt_code_status.config(text=code_msg, foreground="red")
                        messagebox.showerror("Ошибка", f"Неверный код подтверждения: {code_msg}")
                        return
                    else:
                        self.encrypt_code_status.config(text="Код подтвержден", foreground="green")
                else:
                    # Если отправка не удалась, но мессенджер настроен, продолжаем с предупреждением
                    if messagebox.askyesno("Предупреждение", 
                                         f"Не удалось отправить код в мессенджер: {msg}\nПродолжить без подтверждения?"):
                        pass
                    else:
                        return
            
            # Шифрование
            encrypted_data = self.encryption.encrypt_data(data)
            
            # Сохранение в базу данных
            description = f"{data.get('фамилия', '')} {data.get('имя', '')} {data.get('отчество', '')}"
            record_id = self.db_manager.add_record(encrypted_data, data_type, description.strip())
            
            # Отправка уведомления об успешном шифровании
            if self.max_messenger.enabled:
                self.max_messenger.send_operation_notification(
                    "Шифрование данных",
                    "успех",
                    f"Данные {description} успешно зашифрованы. ID записи: {record_id}"
                )
            
            messagebox.showinfo("Успех", "Данные успешно зашифрованы и сохранены")
            self.clear_fields()
            self.encrypt_code_entry.delete(0, tk.END)
            self.encrypt_code_status.config(text="", foreground="black")
            self.update_statistics()
            self.refresh_database()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(e)}")
    
    def decrypt_from_database(self):
        """Дешифрование записи из базы данных"""
        if not self.encryption:
            messagebox.showerror("Ошибка", "Сначала установите пароль")
            return
        
        try:
            record_id = int(self.record_id_entry.get())
            record = self.db_manager.get_record(record_id)
            
            if not record:
                messagebox.showerror("Ошибка", "Запись не найдена")
                return
            
            # Генерация и отправка кода подтверждения
            if self.max_messenger.enabled:
                verification_code = self.code_verification.generate_and_store_code("decrypt", record_id)
                success, msg = self.max_messenger.send_decryption_code(verification_code, record_id)
                
                if success:
                    # Запрос кода подтверждения
                    code_input = self.decrypt_code_entry.get().strip()
                    if not code_input:
                        # Показываем диалог для ввода кода
                        code_dialog = tk.Toplevel(self.root)
                        code_dialog.title("Код подтверждения")
                        code_dialog.geometry("400x150")
                        code_dialog.transient(self.root)
                        code_dialog.grab_set()
                        
                        ttk.Label(code_dialog, 
                                 text=f"Код отправлен в мессенджер MAX.\nВведите код подтверждения:",
                                 font=("Arial", 10)).pack(pady=10)
                        
                        code_entry = ttk.Entry(code_dialog, width=20, font=("Arial", 12))
                        code_entry.pack(pady=5)
                        code_entry.focus()
                        
                        result = {"code": None}
                        
                        def confirm_code():
                            result["code"] = code_entry.get().strip()
                            code_dialog.destroy()
                        
                        ttk.Button(code_dialog, text="Подтвердить", command=confirm_code).pack(pady=5)
                        code_dialog.bind('<Return>', lambda e: confirm_code())
                        
                        code_dialog.wait_window()
                        code_input = result["code"]
                    
                    # Проверка кода
                    is_valid, code_msg = self.code_verification.verify_code(code_input, "decrypt")
                    if not is_valid:
                        self.decrypt_code_status.config(text=code_msg, foreground="red")
                        messagebox.showerror("Ошибка", f"Неверный код подтверждения: {code_msg}")
                        return
                    else:
                        self.decrypt_code_status.config(text="Код подтвержден", foreground="green")
                else:
                    # Если отправка не удалась, но мессенджер настроен, продолжаем с предупреждением
                    if messagebox.askyesno("Предупреждение", 
                                         f"Не удалось отправить код в мессенджер: {msg}\nПродолжить без подтверждения?"):
                        pass
                    else:
                        return
            
            encrypted_data = record["encrypted_data"]
            decrypted_data = self.encryption.decrypt_data(encrypted_data)
            
            # Отображение результата
            result_text = json.dumps(decrypted_data, ensure_ascii=False, indent=2)
            self.decrypted_data_text.delete("1.0", tk.END)
            self.decrypted_data_text.insert("1.0", result_text)
            
            # Отправка уведомления об успешном дешифровании
            if self.max_messenger.enabled:
                self.max_messenger.send_operation_notification(
                    "Дешифрование данных",
                    "успех",
                    f"Данные записи ID {record_id} успешно расшифрованы"
                )
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный ID записи")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании: {str(e)}")
            if self.max_messenger.enabled:
                self.max_messenger.send_operation_notification(
                    "Дешифрование данных",
                    "ошибка",
                    f"Ошибка при дешифровании записи: {str(e)}"
                )
    
    def decrypt_manual(self):
        """Дешифрование данных, введенных вручную"""
        if not self.encryption:
            messagebox.showerror("Ошибка", "Сначала установите пароль")
            return
        
        encrypted_data = self.encrypted_data_text.get("1.0", tk.END).strip()
        
        if not encrypted_data:
            messagebox.showerror("Ошибка", "Введите зашифрованные данные")
            return
        
        try:
            decrypted_data = self.encryption.decrypt_data(encrypted_data)
            result_text = json.dumps(decrypted_data, ensure_ascii=False, indent=2)
            self.decrypted_data_text.delete("1.0", tk.END)
            self.decrypted_data_text.insert("1.0", result_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании: {str(e)}")
    
    def clear_fields(self):
        """Очистка полей ввода"""
        for entry in self.data_fields.values():
            entry.delete(0, tk.END)
    
    def load_from_file(self):
        """Загрузка данных из JSON файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Заполнение полей
            for field_name, entry in self.data_fields.items():
                if field_name in data:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(data[field_name]))
            
            messagebox.showinfo("Успех", "Данные загружены из файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")
    
    def refresh_database(self):
        """Обновление списка записей в базе данных"""
        # Очистка дерева
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Загрузка записей
        records = self.db_manager.get_all_records()
        for record in records:
            created_at = record.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at)
                    created_at = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    pass
            
            self.records_tree.insert("", tk.END, values=(
                record["id"],
                record["type"],
                record.get("description", ""),
                created_at
            ))
        
        self.update_statistics()
    
    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        item = self.records_tree.item(selected[0])
        record_id = item["values"][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись ID {record_id}?"):
            if self.db_manager.delete_record(record_id):
                messagebox.showinfo("Успех", "Запись удалена")
                self.refresh_database()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить запись")
    
    def export_database(self):
        """Экспорт базы данных в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить базу данных",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            import shutil
            shutil.copy(self.db_manager.db_file, file_path)
            messagebox.showinfo("Успех", "База данных экспортирована")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def update_statistics(self):
        """Обновление статистики"""
        stats = self.db_manager.get_statistics()
        stats_text = f"Всего записей: {stats['total_records']}"
        
        if stats['by_type']:
            stats_text += "\nПо типам: "
            for record_type, count in stats['by_type'].items():
                stats_text += f"{record_type}: {count}, "
            stats_text = stats_text.rstrip(", ")
        
        self.stats_label.config(text=stats_text)


def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    app = PersonalDataEncryptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
