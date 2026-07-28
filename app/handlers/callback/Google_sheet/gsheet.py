import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import settings

Account_settings=settings.ACCOUNT_SETTINGS
id_sheet = settings.GOOGLE_SHEET

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

months = {"Январь": 31,"Февраль": 28,"Март": 31,"Апрель": 30,"Май": 31,"Июнь": 30,"Июль": 31,"Август": 31,"Сентябрь": 30,"Октябрь": 31,"Ноябрь": 30,"Декабрь": 31}

async def add_month(month_name):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    spreadsheet.add_worksheet(title=month_name, rows=months[month_name] + 1, cols=6)
    worksheet = spreadsheet.worksheet(month_name)
    worksheet.update([["15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]], 'A1:F1')
async def order_time(month_name, day, time):
    list_time = ['' if x == '0' else '1' for x in list(time)]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)
    worksheet.update(list_time,f'A{day+1}:F{day+1}')


async def get_free_days(month_name):
    """
    Возвращает список дней месяца (int), в которых есть хотя бы один
    свободный (пустой) слот времени.
    Строка 1 листа - заголовок с временем, поэтому день N лежит в строке N+1
    (это соответствует тому, как order_time пишет данные: A{day+1}:F{day+1}).
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    worksheet = spreadsheet.worksheet(month_name)

    all_values = worksheet.get_all_values()
    days_in_month = months[month_name]
    free_days = []

    for day in range(1, days_in_month + 1):
        row_idx = day  # строка day+1 в таблице, но индекс в all_values (0-based) как раз == day
        if row_idx < len(all_values):
            row = all_values[row_idx][:6]
            row += [''] * (6 - len(row))  # добиваем до 6 ячеек, если строка короче
        else:
            row = [''] * 6  # строки вообще нет в ответе - значит день полностью пустой/свободный

        if any(cell.strip() == '' for cell in row):
            free_days.append(day)

    return free_days
