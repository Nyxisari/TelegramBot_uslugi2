import asyncio

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import settings

Account_settings = settings.ACCOUNT_SETTINGS
id_sheet = settings.GOOGLE_SHEET

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

MONTHS_DAYS = {"Январь": 31, "Февраль": 28, "Март": 31, "Апрель": 30, "Май": 31, "Июнь": 30,
               "Июль": 31, "Август": 31, "Сентябрь": 30, "Октябрь": 31, "Ноябрь": 30, "Декабрь": 31}

COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F']

# Семантика ячеек в таблице:
#   ''                          - слот недоступен
#   '1'                         - слот свободен, можно записаться
#   'резервировано @username'   - слот временно удержан на время оплаты
#   '@username'                 - слот оплачен и занят пользователем
RESERVED_PREFIX = "резервировано"

# Один процесс бота - один замок: чтение-изменение-запись строки не пересекаются
# между разными пользователями (иначе два человека могут занять один слот).
_lock = asyncio.Lock()


def reserved_text(display_name: str) -> str:
    return f"{RESERVED_PREFIX} {display_name}"


# ---------------------------------------------------------------- sync-часть

def _spreadsheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(id_sheet)


def _pad(row: list[str]) -> list[str]:
    row = list(row[:6])
    row += [''] * (6 - len(row))
    return row


def _label(header: list[str], i: int) -> str:
    return header[i] if i < len(header) and header[i] else COLUMNS[i]


def _free_days_from_values(all_values: list[list[str]], month_name: str) -> list[int]:
    # Строка 1 - шапка, день N лежит в строке N+1 (индекс N в all_values).
    # gspread обрезает хвостовые пустые строки - отсутствующая строка = нет свободных слотов.
    free_days = []
    for day in range(1, MONTHS_DAYS[month_name] + 1):
        if day >= len(all_values):
            break
        if any(cell.strip() == '1' for cell in _pad(all_values[day])):
            free_days.append(day)
    return free_days


def _add_month(month_name):
    spreadsheet = _spreadsheet()
    worksheet = spreadsheet.add_worksheet(title=month_name, rows=MONTHS_DAYS[month_name] + 1, cols=6)
    worksheet.update([["15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]], 'A1:F1')


def _get_free_months():
    result = []
    for worksheet in _spreadsheet().worksheets():
        if worksheet.title not in MONTHS_DAYS:
            continue
        if _free_days_from_values(worksheet.get_all_values(), worksheet.title):
            result.append(worksheet.title)
    return result


def _get_free_days(month_name):
    worksheet = _spreadsheet().worksheet(month_name)
    return _free_days_from_values(worksheet.get_all_values(), month_name)


def _get_free_times(month_name, day):
    worksheet = _spreadsheet().worksheet(month_name)
    header = worksheet.row_values(1)
    row = _pad(worksheet.row_values(int(day) + 1))
    return [(i, _label(header, i)) for i, cell in enumerate(row) if cell.strip() == '1']


def _set_available_slots(month_name, day, time):
    worksheet = _spreadsheet().worksheet(month_name)
    row_num = int(day) + 1
    header = worksheet.row_values(1)
    current_row = _pad(worksheet.row_values(row_num))
    new_row = current_row.copy()
    opened, already_booked = [], []

    for i in time:
        i = int(i)
        if i < 0 or i > 5:
            continue
        cell_value = current_row[i].strip()
        if cell_value in ('', '1'):
            new_row[i] = '1'
            opened.append(_label(header, i))
        else:
            already_booked.append(_label(header, i))

    if opened:
        worksheet.update([new_row], f'A{row_num}:F{row_num}')
    return opened, already_booked


def _reserve_slots(month_name, day, indices, display_name):
    worksheet = _spreadsheet().worksheet(month_name)
    row_num = int(day) + 1
    header = worksheet.row_values(1)
    current_row = _pad(worksheet.row_values(row_num))

    indices = [int(i) for i in indices if 0 <= int(i) <= 5]
    unavailable = [_label(header, i) for i in indices if current_row[i].strip() != '1']
    if unavailable or not indices:
        return [], unavailable  # бронь всё-или-ничего: если хоть один час занят, ничего не пишем

    new_row = current_row.copy()
    for i in indices:
        new_row[i] = reserved_text(display_name)
    worksheet.update([new_row], f'A{row_num}:F{row_num}')
    return [_label(header, i) for i in indices], []


def _release_slots(month_name, day, indices, display_name):
    """Возвращает '1' только в тех ячейках, где стоит именно бронь этого пользователя."""
    worksheet = _spreadsheet().worksheet(month_name)
    row_num = int(day) + 1
    current_row = _pad(worksheet.row_values(row_num))
    new_row = current_row.copy()
    expected = reserved_text(display_name)
    changed = False

    for i in indices:
        i = int(i)
        if 0 <= i <= 5 and current_row[i].strip() == expected:
            new_row[i] = '1'
            changed = True
    if changed:
        worksheet.update([new_row], f'A{row_num}:F{row_num}')
    return changed


def _finalize_booking(month_name, day, indices, display_name):
    """После оплаты: 'резервировано @user' -> '@user'.
    Если бронь успела сняться по таймеру (слот снова '1') - занимаем его.
    Если слот уже занят кем-то другим - возвращаем False."""
    worksheet = _spreadsheet().worksheet(month_name)
    row_num = int(day) + 1
    current_row = _pad(worksheet.row_values(row_num))
    new_row = current_row.copy()
    expected = reserved_text(display_name)
    ok = True

    for i in indices:
        i = int(i)
        if not 0 <= i <= 5:
            continue
        value = current_row[i].strip()
        if value in (expected, '1', display_name):
            new_row[i] = display_name
        else:
            ok = False
    if new_row != current_row:
        worksheet.update([new_row], f'A{row_num}:F{row_num}')
    return ok


def _release_all_reserved():
    """Старт бота: в памяти броней нет, значит все 'резервировано ...' - зависшие."""
    released = 0
    for worksheet in _spreadsheet().worksheets():
        if worksheet.title not in MONTHS_DAYS:
            continue
        values = worksheet.get_all_values()
        updates = []
        for idx, raw in enumerate(values):
            if idx == 0:
                continue
            row = _pad(raw)
            new_row = ['1' if c.strip().startswith(RESERVED_PREFIX) else c for c in row]
            if new_row != row:
                released += sum(1 for a, b in zip(row, new_row) if a != b)
                updates.append({'range': f'A{idx + 1}:F{idx + 1}', 'values': [new_row]})
        if updates:
            worksheet.batch_update(updates)
    return released


# --------------------------------------------------------------- async-обёртки

async def _run(func, *args):
    async with _lock:
        return await asyncio.to_thread(func, *args)


async def add_month(month_name):
    return await _run(_add_month, month_name)


async def get_free_months() -> list[str]:
    """Названия месяцев (листов), где есть хотя бы один свободный слот."""
    return await _run(_get_free_months)


async def get_free_days(month_name) -> list[int]:
    return await _run(_get_free_days, month_name)


async def get_free_times(month_name, day) -> list[tuple[int, str]]:
    """[(index 0..5, '16:00'), ...] - только слоты со значением '1'."""
    return await _run(_get_free_times, month_name, day)


async def set_available_slots(month_name, day, time):
    """Для админа: открыть слоты ('1'). Чужие брони не перезаписываются.
    Возвращает (opened, already_booked)."""
    return await _run(_set_available_slots, month_name, day, time)


async def reserve_slots(month_name, day, indices, display_name):
    """Временно удерживает слоты ('резервировано @user').
    Возвращает (reserved_labels, unavailable_labels); при непустом unavailable ничего не записано."""
    return await _run(_reserve_slots, month_name, day, indices, display_name)


async def release_slots(month_name, day, indices, display_name):
    """Снимает бронь пользователя, слоты снова '1'."""
    return await _run(_release_slots, month_name, day, indices, display_name)


async def finalize_booking(month_name, day, indices, display_name) -> bool:
    """Оплата прошла: записывает '@user' в ячейки."""
    return await _run(_finalize_booking, month_name, day, indices, display_name)


async def release_all_reserved() -> int:
    return await _run(_release_all_reserved)
