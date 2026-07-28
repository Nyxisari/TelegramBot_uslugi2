from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import settings

Account_settings=settings.ACCOUNT_SETTINGS
id_sheet = settings.GOOGLE_SHEET

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']


def months_names():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(Account_settings, scope)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(id_sheet)
    works = spreadsheet.worksheets()
    keyboard_date = [InlineKeyboardButton(text=x.title, callback_data=x.title) for x in works]
    keyboard_rows = [keyboard_date[x:x+4] for x in range( 0, len(keyboard_date), 4)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows, resize_keyboard=True)
    return keyboard

