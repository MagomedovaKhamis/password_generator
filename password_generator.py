import random
import string
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

# ------------------ Файл для сохранения истории ------------------
HISTORY_FILE = "password_history.json"

# ------------------ Генератор пароля ------------------
def generate_password(length, use_digits, use_letters, use_symbols):
    """Генерирует случайный пароль по заданным параметрам"""
    if not (use_digits or use_letters or use_symbols):
        raise ValueError("Выберите хотя бы один тип символов")
    
    chars = ""
    if use_digits:
        chars += string.digits
    if use_letters:
        chars += string.ascii_letters
    if use_symbols:
        chars += string.punctuation
    
    if length < 1:
        raise ValueError("Длина пароля должна быть не менее 1")
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

# ------------------ Работа с историей (JSON) ------------------
def load_history():
    """Загружает историю из JSON-файла"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """Сохраняет историю в JSON-файл"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def add_to_history(password, length, digits, letters, symbols):
    """Добавляет запись в историю"""
    history = load_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "password": password,
        "length": length,
        "digits": digits,
        "letters": letters,
        "symbols": symbols
    }
    history.append(entry)
    save_history(history)
    return entry

# ------------------ GUI приложение ------------------
class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Переменные
        self.password_length = IntVar(value=12)
        self.use_digits = BooleanVar(value=True)
        self.use_letters = BooleanVar(value=True)
        self.use_symbols = BooleanVar(value=False)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка истории
        self.refresh_history_table()
    
    def create_widgets(self):
        # Рамка настроек
        settings_frame = LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Ползунок длины пароля
        Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_scale = Scale(settings_frame, from_=4, to=32, orient=HORIZONTAL,
                                  variable=self.password_length, length=300)
        self.length_scale.grid(row=0, column=1, padx=10)
        self.length_label = Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2)
        self.length_scale.configure(command=lambda x: self.length_label.configure(text=str(int(x))))
        
        # Чекбоксы
        Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        Checkbutton(settings_frame, text="Спецсимволы (!@#$%...)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")
        
        # Кнопка генерации
        self.generate_btn = Button(self.root, text="Сгенерировать пароль", command=self.on_generate,
                                   bg="green", fg="white", font=("Arial", 10, "bold"))
        self.generate_btn.pack(pady=10)
        
        # Поле для отображения пароля
        self.password_var = StringVar()
        password_frame = Frame(self.root)
        password_frame.pack(fill="x", padx=10, pady=5)
        
        Label(password_frame, text="Сгенерированный пароль:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.password_entry = Entry(password_frame, textvariable=self.password_var, font=("Courier", 11),
                                    state="readonly", readonlybackground="white")
        self.password_entry.pack(fill="x", pady=5)
        
        # Кнопка копирования
        self.copy_btn = Button(password_frame, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=2)
        
        # Таблица истории
        history_frame = LabelFrame(self.root, text="История паролей", padx=5, pady=5)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("timestamp", "password", "length", "digits", "letters", "symbols")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("timestamp", text="Время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("digits", text="Цифры")
        self.tree.heading("letters", text="Буквы")
        self.tree.heading("symbols", text="Символы")
        
        self.tree.column("timestamp", width=130)
        self.tree.column("password", width=220)
        self.tree.column("length", width=50)
        self.tree.column("digits", width=60)
        self.tree.column("letters", width=60)
        self.tree.column("symbols", width=60)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill="both", expand=True)
        scrollbar.pack(side=RIGHT, fill="y")
        
        # ========== КНОПКА ОЧИСТКИ ИСТОРИИ (ДОБАВЛЕНА) ==========
        clear_frame = Frame(self.root)
        clear_frame.pack(fill="x", padx=10, pady=5)
        
        self.clear_btn = Button(clear_frame, text="Очистить историю", command=self.clear_history,
                                bg="red", fg="white", font=("Arial", 9, "bold"))
        self.clear_btn.pack()
    
    def on_generate(self):
        """Обработчик нажатия кнопки генерации"""
        length = self.password_length.get()
        digits = self.use_digits.get()
        letters = self.use_letters.get()
        symbols = self.use_symbols.get()
        
        # Проверка корректности ввода
        if length < 4:
            messagebox.showwarning("Предупреждение", "Минимальная длина пароля - 4 символа. Установлено 4.")
            self.password_length.set(4)
            length = 4
        if length > 32:
            messagebox.showwarning("Предупреждение", "Максимальная длина пароля - 32 символа. Установлено 32.")
            self.password_length.set(32)
            length = 32
        
        try:
            password = generate_password(length, digits, letters, symbols)
            self.password_var.set(password)
            
            # Сохраняем в историю
            add_to_history(password, length, digits, letters, symbols)
            self.refresh_history_table()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def copy_to_clipboard(self):
        """Копирует пароль в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет сгенерированного пароля")
    
    def refresh_history_table(self):
        """Обновляет таблицу истории из JSON"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        history = load_history()
        for entry in history:
            self.tree.insert("", END, values=(
                entry["timestamp"],
                entry["password"],
                entry["length"],
                "Да" if entry["digits"] else "Нет",
                "Да" if entry["letters"] else "Нет",
                "Да" if entry["symbols"] else "Нет"
            ))
    
    def clear_history(self):
        """Очищает историю"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            save_history([])
            self.refresh_history_table()
            messagebox.showinfo("Информация", "История очищена")

# ------------------ Запуск приложения ------------------
if __name__ == "__main__":
    root = Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()