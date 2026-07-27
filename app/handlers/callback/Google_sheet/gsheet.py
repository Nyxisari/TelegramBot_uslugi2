import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import settings

Account_settings=settings.ACCOUNT_SETTINGS
id_sheet = settings.GOOGLE_SHEET

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

async def add_month(month_name, counts_days):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    spreadsheet.add_worksheet(title=month_name, rows=counts_days + 1, cols=6)
    worksheet = spreadsheet.worksheet(month_name)
    worksheet.update([["15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]], 'A1:F1')
async def order_time(month_name, day, time):
    pass
