# User Manual

## Number Base Converter

### Purpose
The application converts integer decimal numbers to bases from 2 through 16. It provides a graphical interface and a console mode, TXT input and output, backup and restoration of the internal character mapping table, and event logging.

### Project files
- `main.py` — starts the GUI or console mode;
- `gui.py` — graphical window and user-action handlers;
- `converter_logic.py` — conversion algorithm, validation, file operations, backups, and logging setup;
- `data/encoding_mapping.json` — internal digit-to-symbol mapping table;
- `backup/` — JSON backup files;
- `logs/app.log` — application log;
- `TZ.docx` — technical specification;
- `Service_Regulation.docx` — maintenance procedure;
- `Test_case.docx` — test cases.

### Requirements
- Python 3.10 or later;
- Tkinter (usually included in the Windows Python installer).

### Starting the application
1. Open the project folder in PyCharm.
2. Open `main.py`.
3. Click **Run**.
4. Wait for the converter window to appear.

To start console mode, run `python main.py --console` in a terminal opened in the project directory.

### Converting a number
1. Enter an integer decimal number, for example `255`.
2. Select a base from `2` to `16`.
3. Click **«Преобразовать»**.
4. For `255` in base `16`, the result is `FF`.

### Loading input from a file
1. Create a UTF-8 text file.
2. Put the decimal integer and base separated by a space, for example `255 16`.
3. Click **«Загрузить из файла»** and select the file.
4. Check the values and conversion result.

If the base is omitted, base `2` is used. Providing both values on the first line is recommended.

### Saving a result
1. Convert the number.
2. Click **«Сохранить результат»**.
3. Select the output folder and TXT filename.
4. Open the file and verify the saved result.

### Backup and restoration
1. Click **«Создать резервную копию»** to save the JSON table in `backup/`.
2. Click **«Восстановить из копии…»** to restore a table.
3. Select a JSON backup file.
4. Confirm replacement of the current table and wait for the success message.

### Logging
Application events are written to `logs/app.log`. Open this file to inspect recent events when troubleshooting.

### Limitations
Only integers are supported. Fractional values and bases outside 2–16 are rejected. The JSON table is internal application data and does not modify operating-system encodings.
