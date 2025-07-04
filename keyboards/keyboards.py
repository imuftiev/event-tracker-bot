import logging

from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from sqlalchemy.orm import sessionmaker

import config
from const.event.chat import Chat
from const.callback.delete import DeleteEvent
from const.event.status import Status
from const.event.priority import Priority
from const.event.repeatable import RepeatType, RepeatDays, OnlyDay
from const.callback.callback_types import InlineButtonType, RepeatTypeInlineButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from const.event.repeatable import RepeatDays
from const.event.update import UpdatePropEvent
from db import engine, Group, User

config = config.BotConfig()
Session = sessionmaker(bind=engine)

"""
    Отметка выбранных дней при напоминании Ежедневно для повторений при создании нового ивента.
"""


def get_days_of_week_keyboard(selected_days: list[str] = None) -> InlineKeyboardMarkup:
    selected_days = selected_days or []
    buttons = []

    for day in RepeatDays:
        is_selected = day.value in selected_days
        text = f"🔸{day.value}" if is_selected else day.value
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=day.value
        )])

    buttons.append([
        InlineKeyboardButton(text=config.confirm, callback_data=InlineButtonType.CONFIRM.value),
        InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


"""
    Отметка выбранных дней при напоминании Ежемесячно для повторений при создании нового ивента.
"""


def get_days_of_month_keyboard(selected_month_days: list[str] = None) -> InlineKeyboardMarkup:
    selected_month_days = selected_month_days or []
    buttons = []

    row = []
    for day in range(1, 32):
        day_str = str(day)
        if day_str in selected_month_days:
            text = f"✅ {day}"
        else:
            text = str(day)

        row.append(
            InlineKeyboardButton(text=text, callback_data=f"day_{day}")
        )

        if len(row) == 4:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text=config.confirm, callback_data=InlineButtonType.CONFIRM.value),
        InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
        InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_months_keyboard(selected_months: list[str] = None) -> InlineKeyboardMarkup:
    selected_months = selected_months or []
    buttons = []

    row = []
    for month in range(1, 13):
        month_str = str(month)
        if month_str in selected_months:
            text = f"✅ {month}"
        else:
            text = str(month)

        row.append(
            InlineKeyboardButton(text=text, callback_data=f"month_{month}")
        )

        if len(row) == 4:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text=config.confirm, callback_data=RepeatTypeInlineButton.CONFIRM_MONTH.value),
        InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
        InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_day_options_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=OnlyDay.TODAY.value, callback_data=OnlyDay.TODAY.value))
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению для отмены действия.
    Работает только в личном чате.
"""


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению для отмены и возврата предыдущего действия.
    Работает только в личном чате.
"""


def get_cancel_return_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению при создании нового ивента при выборе периодичности событий.
    Работает только в личном чате.
"""


def get_repeatable_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text=RepeatType.EVERY_WEEK.value, callback_data=RepeatType.EVERY_WEEK.value),
        types.InlineKeyboardButton(text=RepeatType.EVERY_MONTH.value, callback_data=RepeatType.EVERY_MONTH.value),
        types.InlineKeyboardButton(text=RepeatType.EVERY_YEAR.value, callback_data=RepeatType.EVERY_YEAR.value),
        types.InlineKeyboardButton(text=RepeatType.ONLY_DAY.value, callback_data=RepeatType.ONLY_DAY.value),
        types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value)]
    for button in inline_keyboard:
        builder.row(button)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению при создании нового ивента при выборе приоритета событий.
    Работает только в личном чате.
"""


def get_priority_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text=Priority.LOW.value, callback_data=Priority.LOW.value),
        types.InlineKeyboardButton(text=Priority.MEDIUM.value, callback_data=Priority.MEDIUM.value),
        types.InlineKeyboardButton(text=Priority.HIGH.value, callback_data=Priority.HIGH.value),
        types.InlineKeyboardButton(text=Priority.CRITICAL.value, callback_data=Priority.CRITICAL.value),
    ]
    for button in inline_keyboard:
        builder.row(button)
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


def get_update_status_keyboard(event_id: int) -> InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(
            text=status.value,
            callback_data=f"select_status:{event_id}:{status.name}"
        )
        for status in Status
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])


"""
    Прикрепляется к сообщению при создании нового ивента при выборе статуса событий.
    Работает только в личном чате.
"""


def get_status_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=Status.TO_DO.value, callback_data=Status.TO_DO.value))
    builder.add(types.InlineKeyboardButton(text=Status.PROCESSING.value, callback_data=Status.PROCESSING.value))
    builder.add(types.InlineKeyboardButton(text=Status.DONE.value, callback_data=Status.DONE.value))
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
                types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению при выборе фильтра всех доступных событий.
    Работает только в личном чате.
"""


def get_private_events_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="По статусу", callback_data='status'))
    builder.add(types.InlineKeyboardButton(text="По приоритету", callback_data='priority'))
    builder.add(types.InlineKeyboardButton(text="Все", callback_data="all"))
    builder.row(types.InlineKeyboardButton(text="Групповые", callback_data="group"))
    builder.row(types.InlineKeyboardButton(text="Личный чат", callback_data="private"))
    builder.row(
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value), width=8)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению при выборе фильтра всех доступных событий.
    Работает только в группе.
"""


def get_group_events_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="По статусу", callback_data='status'))
    builder.add(types.InlineKeyboardButton(text="По приоритету", callback_data='priority'))
    builder.add(types.InlineKeyboardButton(text="Все", callback_data="all"))
    builder.row(
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value), width=8)
    return builder.as_markup(resize_keyboard=True)


def get_groups_keyboard(callback: types.CallbackQuery) -> InlineKeyboardMarkup:
    try:
        builder = InlineKeyboardBuilder()
        with Session() as session:
            user = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first()
            groups = session.query(Group).filter_by(user_id=user.id).all()
            for group in groups:
                builder.row(types.InlineKeyboardButton(text=str(group), callback_data=str(group.telegram_group_id)))
            builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
        return builder.as_markup(resize_keyboard=True)
    except Exception as e:
        logging.error(e)


"""
    Прикрепляется к сообщению при выборе куда отправить уведомление, в личный чат или в группу.
    Работает только в личном чате.
"""


def get_chat_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="В этот чат", callback_data=Chat.PRIVATE.value)
    )
    builder.row(
        types.InlineKeyboardButton(text="В группу", callback_data=Chat.GROUP.value)
    )
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
                types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению события при вводе команда /delete.
    Работает только в личном чате.
"""


def get_delete_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Все", callback_data=DeleteEvent.DELETE_ALL.value),
    )
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению события при вызове коллбэк-кнопки Изменить.
    Работает только в личном чате.
"""


def update_event_keyboard(event_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text=UpdatePropEvent.DESCRIPTION.value,
                                   callback_data=f"update_description:{event_id}"),
        types.InlineKeyboardButton(text=UpdatePropEvent.STATUS.value, callback_data=f"update_status:{event_id}"),
        types.InlineKeyboardButton(text=UpdatePropEvent.PRIORITY.value, callback_data=f"update_priority:{event_id}"),
    )
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=f"return_to_event:{event_id}"), width=8)
    return builder.as_markup(resize_keyboard=True)


"""
    Прикрепляется к сообщению события при выводе всех существующих событий.
    Работает только при выводе всех событий в личном чате.
"""


def get_event_action_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить",
                    callback_data=f"update_event:{event_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_event:{event_id}"
                )
            ]
        ]
    )


"""
    Вывод всех прикрепленных пользователем групп.
    Работает только в личном чате.
"""


def get_group_action_keyboard(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_group:{group_id}"
                )
            ]
        ]
    )
