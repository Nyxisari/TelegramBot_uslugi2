from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def times_keyboard(free_times: list[tuple[int, str]], month_name: str, day,
                   selected: list[int] = None) -> InlineKeyboardMarkup:
    """
    free_times - список доступных (index, label), например [(1, '16:00'), (2, '17:00'), (3, '18:00')]
    selected   - список уже выбранных пользователем index (подряд идущих часов)

    Каждая кнопка времени переключает выбор (toggle:...).
    Если выбор не пуст - под кнопками времени появляются "Готово" и "Сбросить".
    """
    selected = selected or []

    buttons = []
    for index, label in free_times:
        text = f"✅ {label}" if index in selected else label
        buttons.append(
            InlineKeyboardButton(text=text, callback_data=f"toggle:{month_name}:{day}:{index}:{label}")
        )
    keyboard_rows = [buttons[x:x + 3] for x in range(0, len(buttons), 3)]

    if selected:
        keyboard_rows.append([
            InlineKeyboardButton(text=f"✅ Готово ({len(selected)} ч.)", callback_data=f"done:{month_name}:{day}"),
            InlineKeyboardButton(text="🔄 Сбросить", callback_data=f"reset:{month_name}:{day}"),
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)