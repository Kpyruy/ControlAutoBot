import time
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup


BOT_TOKEN = '6176635957:AAHYqioHrLiiPsgDVKrUAzQeYe4A9It8eV4'
# message = '⛏ Копать'
# username = 'mine_evo_bot'


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
states = {}

# Определение состояний
class UserInput(StatesGroup):
    message = State()
    username = State()
    back = State()

async def read_settings():
    # Чтение данных из файла settings.txt
    with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    formatted_time = lines[1].split("==")[1].strip()
    stop_count = lines[2].split("==")[1].strip()
    sent_messages = lines[3].split("==")[1].strip()
    return formatted_time, stop_count, sent_messages


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Создание и отправка сообщения с кнопками
    keyboard = types.InlineKeyboardMarkup()
    change_category = types.InlineKeyboardButton(text='🌐 Изменение', callback_data='change_category')
    loop_category = types.InlineKeyboardButton(text='🔄 Цикл', callback_data='loop_category')
    statistics_category = types.InlineKeyboardButton(text='📊 Статистика', callback_data='statistics_category')
    keyboard.add(change_category, loop_category, statistics_category)
    await message.reply("*🪄 Меню управления:*", parse_mode="Markdown", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: True)
async def button_click(callback_query: types.CallbackQuery, state: FSMContext):
    # Получение данных о нажатой кнопке
    button_text = callback_query.data

    keyboard = None  # Объявление переменной keyboard

    if button_text == 'change_category':
        # Создание и отправка сообщения с кнопками категории "Изменение"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Изменить сообщение 📩', callback_data='change_message'))
        keyboard.add(types.InlineKeyboardButton(text='Изменить имя пользователя 👤', callback_data='change_username'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
        await bot.send_message(callback_query.from_user.id, "🌐 Категория *Изменение:*", parse_mode="Markdown", reply_markup=keyboard)

    elif button_text == 'loop_category':
        # Создание и отправка сообщения с кнопками категории "Цикл"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Остановить ⏸️', callback_data='stop'))
        keyboard.add(types.InlineKeyboardButton(text='Возобновить ▶️', callback_data='resume'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
        await bot.send_message(callback_query.from_user.id, "🔄 Категория *Цикл:*", parse_mode="Markdown", reply_markup=keyboard)

    elif button_text == 'statistics_category':
        # Создание и отправка сообщения с кнопками категории "Статистика"
        formatted_time, stop_count, sent_messages = await read_settings()
        statistics = f"⌛ Общее время работы бота: *{formatted_time}*\n📨 Количество отправленных сообщений: *{sent_messages}*\n🛑 Количество остановок: *{stop_count}*"
        keyboard = types.InlineKeyboardMarkup()
        refresh_button = types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_statistics')
        logs_button = types.InlineKeyboardButton(text='Логи 🔣', callback_data='logs')
        keyboard.add(refresh_button, logs_button)
        await bot.send_message(callback_query.from_user.id, statistics, parse_mode="Markdown", reply_markup=keyboard)

    elif button_text == 'change_message':
        await bot.answer_callback_query(callback_query.id, text="📩 Введите новое сообщение:")
        await UserInput.message.set()  # Установка состояния UserInput.message
        await state.update_data(keyboard=keyboard)  # Сохранение значения keyboard в состояние

    elif button_text == 'change_username':
        await bot.answer_callback_query(callback_query.id, text="✏️ Введите имя в чат:")
        await UserInput.username.set()  # Установка состояния UserInput.username
        await state.update_data(keyboard=keyboard)  # Сохранение значения keyboard в состояние

    elif button_text == 'stop':
        # Чтение текущих значений из файла
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        # Изменение значения "Pause" на True
        for i, line in enumerate(lines):
            if line.startswith('Pause'):
                lines[i] = 'Pause==True\n'
        # Запись измененных значений обратно в файл
        with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)
        await bot.answer_callback_query(callback_query.id, text="⏸️ Отправка сообщений остановлена!")

    elif button_text == 'resume':
        # Чтение текущих значений из файла
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        # Изменение значения "Pause" на False
        for i, line in enumerate(lines):
            if line.startswith('Pause'):
                lines[i] = 'Pause==False\n'
        # Запись измененных значений обратно в файл
        with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)
        await bot.answer_callback_query(callback_query.id, text="▶️ Отправка сообщений возобновлена!")

    elif button_text == 'refresh_statistics':
        formatted_time, stop_count, sent_messages = await read_settings()
        statistics = f"⌛ Общее время работы бота: *{formatted_time}*\n📨 Количество отправленных сообщений: *{sent_messages}*\n🛑 Количество остановок: *{stop_count}*"
        keyboard = types.InlineKeyboardMarkup()
        refresh_button = types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_statistics')
        logs_button = types.InlineKeyboardButton(text='Логи 🔣', callback_data='logs')
        keyboard.add(refresh_button, logs_button)
        if statistics != callback_query.message.text or keyboard != callback_query.message.reply_markup:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, text=statistics,
                                        parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

    elif button_text == 'logs':
        # Добавьте ваш функционал для загрузки логов
        await bot.answer_callback_query(callback_query.id, text="Загрузка логов...")

    elif button_text == 'back':
        await bot.answer_callback_query(callback_query.id, text="Вы успешно вернулись в меню! 🎊")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)  # Удаление сообщения

        await state.finish()  # Завершение состояния


@dp.message_handler(state=UserInput.message)
async def update_message (message: types.Message, state: FSMContext):
    # Обновление сообщения
    with open('head/values/message.txt', 'w', encoding='utf-8-sig') as file:
        file.write(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()  # Завершение состояния

    # Уведомление об изменении сообщения
    await bot.send_message(chat_id=message.chat.id, text=f"✉️ Сообщение изменено на: {message.text}")


@dp.message_handler(state=UserInput.username)
async def update_username (message: types.Message, state: FSMContext):
    # Обновление имени пользователя
    with open('head/values/username.txt', 'w', encoding='utf-8-sig') as file:
        file.write(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()  # Завершение состояния

    # Уведомление об изменении имени пользователя
    await bot.send_message(chat_id=message.chat.id, text=f"👁️ Имя пользователя изменено на: {message.text}")


async def main():
    # Запуск бота
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())