"""Функциональный модуль конвертера: преобразование, файлы и резервные копии.\n\nЗдесь размещена логика, не зависящая от графического интерфейса. Благодаря этому\nфункции можно проверять автоматически отдельно от окна Tkinter.\n"""
import json
from datetime import datetime
from pathlib import Path
# Определяем корень проекта относительно расположения этого файла, а не
# текущей рабочей папки. Поэтому приложение можно запускать и из PyCharm,
# и из терминала, открытого в другом каталоге.
BASE_DIR = Path(__file__).resolve().parent
from logger import logger


# Индекс символа в этой строке соответствует остатку от деления на основание.
# Для оснований 11–16 после цифр 0–9 используются буквы A–F.
DIGITS = "0123456789ABCDEF"
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"
MAPPING_FILE = DATA_DIR / "encoding_mapping.json"

def decimal_to_base(number: int, base: int) -> str:
    """Переводит целое десятичное число в систему с основанием 2–16."""
    # Проверяем основание до вычислений: поддерживаются только значения 2–16.
    if not 2 <= base <= 16:
        logger.warning("Недопустимое основание: %s", base)
        raise ValueError("Основание системы счисления должно быть от 2 до 16.")
    # Ноль требует отдельной обработки: цикл деления для него не выполнится.
    if number == 0:
        return "0"

    # Отрицательное число преобразуем по модулю, а знак добавим в конце.
    sign = "-" if number < 0 else ""
    number = abs(number)
    digits = []
    while number:
        # Остатки получаются справа налево, поэтому ниже список переворачивается.
        number, remainder = divmod(number, base)
        digits.append(DIGITS[remainder])
    return sign + "".join(reversed(digits))

def convert_text(number_text: str, base: int) -> str:
    """Проверяет ввод и преобразует десятичное целое число."""
    # Удаляем пробелы по краям, чтобы ввод " 25 " обрабатывался как 25.
    number_text = number_text.strip()
    if not number_text:
        logger.warning("Пустое значение для преобразования")
        raise ValueError("Введите целое десятичное число.")
    try:
        number = int(number_text, 10)
    except ValueError as exc:
        logger.warning("Некорректное десятичное число: %r", number_text)
        raise ValueError("Число должно быть целым и записанным в десятичной системе.") from exc
    result = decimal_to_base(number, base)
    logger.info("Преобразование: число=%s, основание=%s, результат=%s", number, base, result)
    return result

def ensure_mapping_file():
    """Создаёт внутреннюю JSON-таблицу, если её ещё нет."""
    # Не перезаписываем существующую таблицу, чтобы сохранить пользовательские данные.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MAPPING_FILE.exists():
        data = {"digits": {str(i): DIGITS[i] for i in range(16)}, "bases_supported": list(range(2, 17)), "updated_at": datetime.now().isoformat(timespec="seconds")}
        MAPPING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Создана таблица соответствия: %s", MAPPING_FILE)

def backup_mapping() -> Path:
    """Создаёт отдельную копию JSON-таблицы и возвращает путь к ней."""
    ensure_mapping_file()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    # Время в имени позволяет различать копии, созданные в разные моменты.
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"encoding_mapping_{stamp}.json"
    i = 1
    while target.exists():
        target = BACKUP_DIR / f"encoding_mapping_{stamp}_{i}.json"
        i += 1
    target.write_bytes(MAPPING_FILE.read_bytes())
    logger.info("Создана резервная копия: %s", target)
    return target

def restore_mapping(backup_path):
    """Восстанавливает таблицу из выбранной JSON-копии после проверки файла."""
    path = Path(backup_path)
    if not path.is_file():
        logger.error("Файл резервной копии не найден: %s", path)
        raise FileNotFoundError(f"Файл резервной копии не найден: {path}")
    # Сначала читаем и разбираем JSON: некорректный файл не будет записан как текст.
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Резервная копия имеет неверный формат.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MAPPING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Таблица восстановлена из резервной копии: %s", path)

def read_input_file(path):
    """Читает число и необязательное основание из текстового файла.

    Пример содержимого: 255 16. Если основание не указано, используется 2.
    """
    content = Path(path).read_text(encoding="utf-8").strip()
    parts = content.replace(",", " ").split()
    if not parts:
        raise ValueError("Файл пуст.")
    number = parts[0]
    base = int(parts[1]) if len(parts) >= 2 else 2
    if not 2 <= base <= 16:
        raise ValueError("В файле основание должно быть от 2 до 16.")
    return number, base

def write_output_file(path, result):
    """Сохраняет результат преобразования в UTF-8 с переводом строки в конце."""
    Path(path).write_text(str(result).rstrip() + "\n", encoding="utf-8")
    logger.info("Результат сохранён в файл: %s", path)
