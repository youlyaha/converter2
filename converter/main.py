"""Исполнительный модуль приложения.

По умолчанию запускает графическое окно. Аргумент --console включает
альтернативный консольный режим, удобный для быстрой проверки логики.
"""
import sys
from converter_logic import convert_text
from gui import ConverterApp
from converter_logic import logger


def run_console():
    """Запускает простой диалог преобразования в терминале."""
    logger.info("Программа запущена в консольном режиме")
    while True:
        try:
            # Буква q позволяет завершить цикл без аварийного прерывания.
            raw = input("Введите десятичное целое число (или q для выхода): ").strip()
            if raw.lower() == "q":
                logger.info("Программа закрыта пользователем в консольном режиме")
                break
            base = int(input("Введите основание (2–16): ").strip())
            print("Результат:", convert_text(raw, base))
        except (ValueError, EOFError) as exc:
            # Ошибка ввода показывается пользователю, после чего диалог продолжается.
            logger.error("Ошибка в консольном режиме: %s", exc)
            print("Ошибка:", exc)


if __name__ == "__main__":
    # Режим выбирается параметром командной строки; без него открывается GUI.
    if "--console" in sys.argv:
        run_console()
    else:
        ConverterApp().mainloop()
