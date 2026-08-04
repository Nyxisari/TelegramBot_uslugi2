import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import settings

Account_settings=settings.ACCOUNT_SETTINGS
id_sheet = settings.GOOGLE_SHEET

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

MONTHS_DAYS = {"Январь": 31,"Февраль": 28,"Март": 31,"Апрель": 30,"Май": 31,"Июнь": 30,"Июль": 31,"Август": 31,"Сентябрь": 30,"Октябрь": 31,"Ноябрь": 30,"Декабрь": 31}


async def add_month(month_name):
    months = MONTHS_DAYS
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    spreadsheet.add_worksheet(title=month_name, rows=months[month_name] + 1, cols=6)
    worksheet = spreadsheet.worksheet(month_name)
    worksheet.update([["15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]], 'A1:F1')


COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F']


async def get_free_times(month_name, day):
    """
    Возвращает список слотов, доступных для записи в конкретный день.
    Каждый элемент - кортеж (index, label):
      index - индекс столбца, 0..5 (нужен для order_time)
      label - подпись времени из шапки листа, например '16:00'

    Слот считается доступным, если в ячейке стоит ровно '1'
    (см. семантику ячеек в order_time / get_free_days).
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)

    day = int(day)
    row_num = day + 1
    header = worksheet.row_values(1)
    row = worksheet.row_values(row_num)
    row += [''] * (6 - len(row))

    free_times = []
    for i, cell in enumerate(row[:6]):
        if cell.strip() == '1':
            label = header[i] if i < len(header) else COLUMNS[i]
            free_times.append((i, label))
    print(free_times)
    return free_times


async def set_available_slots(month_name, day, time):
    """
    Проставляет '1' (слот доступен для записи) в выбранные ячейки дня.
    Предназначена для тебя/админа - чтобы вручную открывать слоты для записи.

    month_name - название листа (месяца)
    day        - номер дня месяца (int)
    time       - список индексов слотов, которые нужно сделать доступными,
                 int, 0..5 (0 = столбец A/15:00, ..., 5 = F/20:00)
                 пример: [0, 1, 2] -> откроет 15:00, 16:00, 17:00

    Семантика ячеек в таблице:
      ''            - слот недоступен, бронировать нельзя
      '1'           - слот доступен, можно забронировать
      '@username'   - слот уже занят этим пользователем

    Ячейки, где уже есть чья-то бронь ('@username'), НЕ перезаписываются -
    чтобы случайно не стереть существующую запись клиента. Такие слоты
    попадут в already_booked. Ячейки, уже равные '1', остаются '1' и тоже
    считаются успешно обработанными.

    Возвращает кортеж (opened, already_booked):
      opened          - список времени, которые стали/остались доступны ('1')
      already_booked  - список времени, где уже стояла чья-то бронь -
                        их пришлось пропустить
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)

    day = int(day)  # на случай, если day пришёл строкой
    row_num = day + 1
    header = worksheet.row_values(1)  # ["15:00", "16:00", ...] - для читаемых названий в ответе
    current_row = worksheet.row_values(row_num)
    current_row += [''] * (6 - len(current_row))

    new_row = current_row.copy()
    opened, already_booked = [], []

    for i in time:
        i = int(i)
        if i < 0 or i > 5:
            continue  # индекс вне диапазона столбцов A..F - игнорируем

        time_label = header[i] if i < len(header) else COLUMNS[i]
        cell_value = current_row[i].strip()

        if cell_value == '' or cell_value == '1':
            new_row[i] = '1'
            opened.append(time_label)
        else:
            # там уже что-то не '' и не '1' - считаем это чужой бронью, не трогаем
            already_booked.append(time_label)

    if opened:
        worksheet.update([new_row], f'A{row_num}:F{row_num}')

    return opened, already_booked


async def order_time(month_name, day, time, username):
    """
    Бронирует выбранные пользователем слоты времени на конкретный день.
    Обновление отправляется одним запросом на всю строку (A{row}:F{row}),
    а не отдельными вызовами на каждую ячейку.

    month_name - название листа (месяца)
    day        - номер дня месяца (int)
    time       - список индексов выбранных слотов, int, 0..5
                 (0 = столбец A/15:00, 1 = B/16:00, ..., 5 = F/20:00)
                 пример: [1, 3] -> выбраны 16:00 и 18:00
    username   - имя пользователя телеграм, которое будет записано в ячейку
                 (с '@' или без - '@' будет добавлен автоматически)

    Семантика ячеек в таблице:
      ''            - слот недоступен, бронировать нельзя
      '1'           - слот доступен, можно забронировать
      '@username'   - слот уже занят этим пользователем

    Бронируются только те выбранные слоты, которые на данный момент
    реально доступны (значение в таблице == '1'). Ячейки, не входящие
    в выбор пользователя, остаются без изменений - для этого текущая
    строка сначала читается, в ней меняются только нужные позиции,
    и затем вся строка целиком записывается обратно одним запросом.

    Возвращает кортеж (booked, unavailable):
      booked      - список времени (заголовков колонок из строки 1),
                    которые удалось забронировать
      unavailable - список времени, которые выбрал пользователь,
                    но забронировать не вышло (уже заняты/недоступны)
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)

    day = int(day)  # на случай, если day пришёл строкой из callback_data
    row_num = day + 1
    header = worksheet.row_values(1)  # ["15:00", "16:00", ...] - для читаемых названий в ответе
    current_row = worksheet.row_values(row_num)
    current_row += [''] * (6 - len(current_row))

    new_row = current_row.copy()
    display_name = username if str(username).startswith('@') else f'@{username}'

    booked, unavailable = [], []

    for i in time:
        i = int(i)
        if i < 0 or i > 5:
            continue  # индекс вне диапазона столбцов A..F - игнорируем

        time_label = header[i] if i < len(header) else COLUMNS[i]

        if current_row[i].strip() == '1':
            new_row[i] = display_name
            booked.append(time_label)
        else:
            unavailable.append(time_label)

    if booked:
        worksheet.update([new_row], f'A{row_num}:F{row_num}')

    return booked, unavailable


async def get_free_days(month_name):
    """
    Возвращает список дней месяца (int), в которых есть хотя бы один
    слот, доступный для записи.

    Семантика ячеек в таблице:
      ''            - слот недоступен, записаться нельзя
      '1'           - слот доступен, можно записаться
      '@username'   - слот уже занят этим пользователем

    Строка 1 листа - заголовок с временем, поэтому день N лежит в строке N+1
    (это соответствует тому, как order_time пишет данные: A{day+1}:F{day+1}).

    ВАЖНО: worksheet.get_all_values() обрезает хвостовые полностью пустые
    строки листа - если для дня в конце месяца ещё ни одна ячейка не
    заполнена, gspread такую строку вообще не вернёт. Раньше при такой
    "пустой по умолчанию" строке день считался свободным, но при новой
    семантике пустая ячейка = "нельзя записаться", поэтому отсутствующая
    строка тоже означает, что свободных слотов в этот день нет.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)

    all_values = worksheet.get_all_values()
    days_in_month = MONTHS_DAYS[month_name]
    free_days = []

    for day in range(1, days_in_month + 1):
        row_idx = day  # строка day+1 в таблице, но индекс в all_values (0-based) как раз == day
        if row_idx >= len(all_values):
            continue  # строки нет вообще - значит доступных слотов в этот день нет

        row = all_values[row_idx][:6]
        row += [''] * (6 - len(row))  # добиваем до 6 ячеек, если строка короче

        if any(cell.strip() == '1' for cell in row):
            free_days.append(day)

    return free_days