"""Графический модуль приложения на Tkinter.

Этот файл отвечает за окно, поля ввода, кнопки и сообщения пользователю.
Сами вычисления и операции с файлами выполняются функциями из converter_logic.py.
"""
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from converter_logic import (convert_text, ensure_mapping_file, backup_mapping, restore_mapping, BACKUP_DIR, BASE_DIR, read_input_file, write_output_file)
from converter_logic import logger
APP_TITLE = "Конвертер систем счисления"

class ConverterApp(tk.Tk):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("680x520")
        self.minsize(600, 470)
        ensure_mapping_file()
        logger.info("Программа запущена в графическом режиме")
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self._build_ui()

    def close_app(self):
        logger.info("Программа закрыта")
        self.destroy()

    def _build_ui(self):
        """Создаёт и размещает все элементы интерфейса."""
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=APP_TITLE, font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(root, text="Перевод целых десятичных чисел в системы счисления с основаниями от 2 до 16.").pack(anchor="w", pady=(4, 16))

        form = ttk.LabelFrame(root, text="Параметры преобразования", padding=12)
        form.pack(fill="x")
        ttk.Label(form, text="Десятичное целое число:").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        self.number_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.number_var, width=30).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Label(form, text="Основание (2–16):").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        self.base_var = tk.IntVar(value=2)
        ttk.Combobox(form, textvariable=self.base_var, values=list(range(2, 17)), state="readonly", width=27).grid(row=1, column=1, sticky="ew", pady=6)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Преобразовать", command=self.convert).pack(side="left")
        ttk.Button(actions, text="Загрузить из файла", command=self.load_input).pack(side="left", padx=8)
        ttk.Button(actions, text="Сохранить результат", command=self.save_output).pack(side="left")

        result_frame = ttk.LabelFrame(root, text="Результат", padding=12)
        result_frame.pack(fill="x")
        self.result_var = tk.StringVar(value="Здесь появится результат.")
        ttk.Label(result_frame, textvariable=self.result_var, font=("Consolas", 15, "bold"), wraplength=580).pack(anchor="w")

        file_frame = ttk.LabelFrame(root, text="Резервное копирование таблицы соответствия", padding=12)
        file_frame.pack(fill="x", pady=(12, 0))
        ttk.Label(file_frame, text=f"Файл таблицы: data/encoding_mapping.json\nРезервные копии сохраняются в папке: backup").pack(anchor="w")
        backup_actions = ttk.Frame(file_frame)
        backup_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(backup_actions, text="Создать резервную копию", command=self.make_backup).pack(side="left")
        ttk.Button(backup_actions, text="Восстановить из копии…", command=self.restore_backup).pack(side="left", padx=8)
        self.bind("<Return>", lambda _event: self.convert())

    def convert(self):
        """Проверяет поля, запускает преобразование и показывает результат."""
        try:
            base = int(self.base_var.get())
            result = convert_text(self.number_var.get(), base)
        except (ValueError, TypeError) as exc:
            logger.error("Ошибка преобразования из интерфейса: %s", exc)
            messagebox.showerror("Ошибка ввода", str(exc))
            return
        self.result_var.set(f"{self.number_var.get().strip()}₁₀ = {result} (основание {base})")

    def load_input(self):
        """Открывает диалог выбора TXT-файла и заполняет поля данными."""
        path = filedialog.askopenfilename(title="Выберите текстовый файл с десятичным числом", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Загрузка входного файла отменена")
            return
        try:
            number, base = read_input_file(path)
            self.number_var.set(number)
            self.base_var.set(base)
            logger.info("Входные данные загружены из файла: %s", path)
            self.convert()
        except (OSError, ValueError) as exc:
            logger.exception("Ошибка чтения файла %s", path)
            messagebox.showerror("Ошибка чтения файла", str(exc))

    def save_output(self):
        """Сохраняет показанный результат в файл, выбранный пользователем."""
        result = self.result_var.get()
        if result == "Здесь появится результат.":
            logger.warning("Попытка сохранить результат до преобразования")
            messagebox.showwarning("Нет результата", "Сначала выполните преобразование.")
            return
        path = filedialog.asksaveasfilename(title="Сохранить результат", defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Сохранение результата отменено")
            return
        try:
            write_output_file(path, result)
            logger.info("Результат сохранён в файл: %s", path)
            messagebox.showinfo("Готово", f"Результат сохранён в файл:\n{path}")
        except OSError as exc:
            logger.exception("Ошибка сохранения результата в %s", path)
            messagebox.showerror("Ошибка сохранения", str(exc))

    def make_backup(self):
        """Создаёт резервную копию таблицы и сообщает путь к файлу."""
        try:
            path = backup_mapping()
            messagebox.showinfo("Резервная копия создана", f"Файл сохранён:\n{path}")
        except OSError as exc:
            logger.exception("Ошибка создания резервной копии")
            messagebox.showerror("Ошибка резервного копирования", str(exc))

    def restore_backup(self):
        """Запрашивает копию, подтверждение пользователя и восстанавливает JSON."""
        path = filedialog.askopenfilename(title="Выберите резервную копию таблицы", initialdir=str(BACKUP_DIR) if BACKUP_DIR.exists() else str(BASE_DIR), filetypes=[("JSON-файлы", "*.json"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Выбор резервной копии отменён")
            return
        if not messagebox.askyesno("Подтверждение", "Заменить текущую таблицу соответствия выбранной копией?"):
            logger.info("Пользователь отказался от восстановления таблицы")
            return
        try:
            restore_mapping(path)
            messagebox.showinfo("Восстановление завершено", "Таблица соответствия успешно восстановлена.")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            logger.exception("Ошибка восстановления из %s", path)
            messagebox.showerror("Ошибка восстановления", str(exc))

