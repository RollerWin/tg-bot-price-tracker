from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.repositories import (user as user_repo,
                                   check_interval as check_interval_repo)
from bot.keyboards import menu_keyboards as menu_kb

user = Router()


class Registration(StatesGroup):
    username = State()
    interval = State()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if await user_repo.is_user_exists(message.from_user.id):
        user_info = await user_repo.get_user_info(message.from_user.id)
        await message.answer(await write_info(user_info), reply_markup=menu_kb.main_menu)
    else:
        await message.answer("Приветствуем в боте по отслеживанию цен!\n"
                             "Подскажите, как к вам можно обращаться?")
        await state.set_state(Registration.username)


@user.message(Registration.username)
async def register_username(message: Message, state: FSMContext):
    await state.set_state(Registration.interval)
    await state.update_data(username=message.text)
    await message.answer("Какой интервал обновления цен вы бы хотели установить?",
                         reply_markup=menu_kb.interval_values
                         )


@user.callback_query(Registration.interval)
async def register_username(call: CallbackQuery, state: FSMContext):
    info = await state.get_data()
    await state.clear()

    user_id = call.from_user.id
    interval = int(call.data)
    await user_repo.add_user(user_id, info['username'])
    await check_interval_repo.add_check_interval(user_id, interval)
    user_info = await user_repo.get_user_info(user_id)

    await call.message.answer(f"Вы успешно зарегистрировались!\n\n"
                                 f"{await write_info(user_info)}",
                                 reply_markup=menu_kb.main_menu)


async def write_info(user_info):
    text = (f"Добро пожаловать, {user_info.username} !\n\n"
            f"Чем займёмся сегодня?")
    return text
