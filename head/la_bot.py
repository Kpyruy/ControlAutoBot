import os
import time
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from configparser import ConfigParser

config = ConfigParser()
config.read('private/.env')

BOT_TOKEN = config.get('BOT', 'TOKEN')

#BOT_TOKEN = '6176635957:AAHYqioHrLiiPsgDVKrUAzQeYe4A9It8eV4'
# message = '⛏ Копать'
# username = 'mine_evo_bot'
last_button_press = {}

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
states = {}

# Определение состояний
class UserInput(StatesGroup):
    message = State()
    username = State()
    message_count = State()
    message_auto = State()
    back = State()

async def send_notification():
    # Здесь вы можете настроить текст сообщения и получателя
    send_notification = "*Сообщения были успешно отправленны!* 💫"
    keyboard = types.InlineKeyboardMarkup()
    done_button = types.InlineKeyboardButton(text='Выполнено! ✅', callback_data='done')
    keyboard.row(done_button)
    await bot.send_message(callback_query.from_user.id, send_notification, parse_mode="Markdown", reply_markup=keyboard)

async def write_message_content():
    _, _, message_auto = await read_autosend()
    message_content = message_auto
    with open('head/values/message.txt', 'w', encoding='utf-8-sig') as file:
        file.write(f"{message_content}")

async def write_residual():
    with open('head/values/residual_message.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    residual_message = lines[0]
    with open('head/values/message.txt', 'w', encoding='utf-8-sig') as file:
        file.write(f"{residual_message}")

async def read_autosend():
    with open('head/values/autosend_data.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    message_auto = lines[0].split("==")[1].strip()
    message_count = lines[1].split("==")[1].strip()
    with open('head/values/autosend.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    autosend = lines[0].split("==")[1].strip()
    return autosend, message_count, message_auto

async def write_autosend_content(message_auto):
    with open('head/values/autosend_data.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    lines[0] = f"message_auto=={message_auto}\n"
    with open('head/values/autosend_data.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)

async def write_autosend_count(message_count):
    with open('head/values/autosend_data.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    lines[1] = f"message_count=={message_count}\n"
    with open('head/values/autosend_data.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)

async def write_autosend(autosend):
    with open('head/values/autosend.txt', 'w', encoding='utf-8') as file:
        file.write(f"autosend=={autosend}\n")

async def read_remaining_messages():
    with open('head/values/remaining_messages.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    specified_messages = int(lines[0].split("==")[1].strip())
    return specified_messages

async def write_remaining_messages(specified_number_messages):
    with open('head/values/remaining_messages.txt', 'w', encoding='utf-8') as file:
        file.write(f"remaining_messages=={specified_number_messages}\n")

async def read_new_value():
    with open('head/values/new_message_value.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    last_of_messages = lines[0].split("==")[1].strip()
    return last_of_messages

async def read_settings():
    # Чтение данных из файла settings.txt
    with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    formatted_time = lines[0].split("==")[1].strip()
    stop_count = lines[1].split("==")[1].strip()
    sent_messages = lines[2].split("==")[1].strip()
    return formatted_time, stop_count, sent_messages

async def read_flood():
    # Чтение данных из файла settings.txt
    with open('head/values/flood_wait.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    flood_wait = int(lines[0].split("==")[1].strip())
    return flood_wait

async def read_logs():
    with open('head/values/logs.txt', 'r', encoding='utf-8') as file:
        logs = file.readlines()
    return logs

async def show_logs(callback_query, state):
    logs = await read_logs()
    data = await state.get_data()
    index = data.get('logs_index', 0)
    limit = 10
    message_text = "*Последние активные логи:*\n```"
    for line in logs[index:index + limit]:
        timestamp_end_index = line.index("]")
        timestamp = line[1:timestamp_end_index]
        log_text = line[timestamp_end_index + 2:]
        message_text += f"[{timestamp}] {log_text}"
    message_text += "```"
    keyboard = types.InlineKeyboardMarkup()
    prev_button = types.InlineKeyboardButton(text='◀️ Назад', callback_data='prev_logs')
    next_button = types.InlineKeyboardButton(text='Вперед ▶️', callback_data='next_logs')
    done_button = types.InlineKeyboardButton(text='Выполнено! ✅', callback_data='done')
    keyboard.row(prev_button, next_button)
    keyboard.row(done_button)
    # Проверка, изменилось ли содержимое сообщения или разметка ответа
    if (callback_query.message.text == message_text and
            callback_query.message.reply_markup == keyboard):
        return
    # Редакция существующего сообщения с новыми логами
    await callback_query.bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=message_text, parse_mode="Markdown", reply_markup=keyboard)

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
        keyboard.add(types.InlineKeyboardButton(text='Авто-отправка 💠', callback_data='autosend'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
        await bot.send_message(callback_query.from_user.id, "🔄 Категория *Цикл:*", parse_mode="Markdown", reply_markup=keyboard)

    elif button_text == 'statistics_category':
        # Создание и отправка сообщения с кнопками категории "Статистика"
        formatted_time, stop_count, sent_messages = await read_settings()
        flood_wait = await read_flood()
        statistics = f"⌛ Общее время работы бота: *{formatted_time}*\n📨 Количество отправленных сообщений: *{sent_messages}*\n🛑 Количество остановок: *{stop_count}*"
        if flood_wait > 0:
            statistics += f"\n\n🕒 Отсчет времени FloodWait: *{flood_wait}*"
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
        with open('head/values/pause.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        # Изменение значения "Pause" на True
        for i, line in enumerate(lines):
            if line.startswith('Pause'):
                lines[i] = 'Pause==True\n'
        # Запись измененных значений обратно в файл
        with open('head/values/pause.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)
        await bot.answer_callback_query(callback_query.id, text="⏸️ Отправка сообщений остановлена!")

    elif button_text == 'resume':
        # Чтение текущих значений из файла
        with open('head/values/pause.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        # Изменение значения "Pause" на False
        for i, line in enumerate(lines):
            if line.startswith('Pause'):
                lines[i] = 'Pause==False\n'
        # Запись измененных значений обратно в файл
        with open('head/values/pause.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)
        await bot.answer_callback_query(callback_query.id, text="▶️ Отправка сообщений возобновлена!")

    # Обработчик действия для кнопки "refresh_statistics"
    elif button_text == 'refresh_statistics':
        # Получение времени последнего нажатия для данного пользователя
        last_press_time = last_button_press.get(callback_query.from_user.id, 0)
        # Проверка, прошла ли секунда с момента последнего нажатия
        if time.time() - last_press_time < 1.5:
            # Если прошла менее секунды, отправляем уведомление о задержке
            await bot.answer_callback_query(callback_query.id, text="❌ Упс... Данные ещё не обновились!")
            return
        formatted_time, stop_count, sent_messages = await read_settings()
        flood_wait = await read_flood()
        statistics = f"⌛ Общее время работы бота: *{formatted_time}*\n📨 Количество отправленных сообщений: *{sent_messages}*\n🛑 Количество остановок: *{stop_count}*"
        if flood_wait > 0:
            statistics += f"\n\n🕒 Отсчет времени FloodWait: *{flood_wait}*"
        keyboard = types.InlineKeyboardMarkup()
        refresh_button = types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_statistics')
        logs_button = types.InlineKeyboardButton(text='Логи 🔣', callback_data='logs')
        keyboard.add(refresh_button, logs_button)
        if statistics != callback_query.message.text or keyboard != callback_query.message.reply_markup:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, text=statistics,
                                        parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

        # Обновление времени последнего нажатия для данного пользователя

        last_button_press[callback_query.from_user.id] = time.time()
    elif button_text == 'logs':
        await show_logs(callback_query, state)

    elif button_text == 'prev_logs':
        data = await state.get_data()
        index = data.get('logs_index', 0)
        limit = 10
        has_prev_logs = index > 0
        if not has_prev_logs:
            await bot.answer_callback_query(callback_query.id, text="📑 Вы уже в самом начале!")
            return
        logs = await read_logs()
        if index >= limit:
            index -= limit
        await state.update_data(logs_index=index)
        await callback_query.answer()
        await bot.answer_callback_query(callback_query.id, text="Загрузка логов... ⏱️")
        await show_logs(callback_query, state)

    elif button_text == 'next_logs':
        data = await state.get_data()
        logs = await read_logs()
        index = data.get('logs_index', 0)
        limit = 10
        has_next_logs = (index + limit) < len(logs)
        if not has_next_logs:
            await bot.answer_callback_query(callback_query.id, text="📑 Следующих логов ещё нет, пожалуйста, подождите.")
            return  # Return here to avoid editing the message
        if index + limit < len(logs):
            index += limit
        await state.update_data(logs_index=index)
        await callback_query.answer()
        await bot.answer_callback_query(callback_query.id, text="Загрузка логов... ⏱️")
        new_message_text = "\n".join(logs[index:index + limit])  # Replace with your logic to generate the message text
        if new_message_text != callback_query.message.text:
            await show_logs(callback_query, state)
        else:
            return

    elif button_text == 'autosend':
        autosend, message_count, message_auto = await read_autosend()
        last_of_messages = await read_new_value()
        if autosend == 'True':
            autosend_message = f"❇️ Авто-отправка запущена!\n\n🧭 Заданное количество сообщений: {message_count}\n⛽️ Заданный текст: {message_auto}\n🪂 Осталось сообщений: {last_of_messages}"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_autosend'))
            keyboard.add(types.InlineKeyboardButton(text='Выключить ❌️', callback_data='decline'))
        else:
            autosend_message = "💢 Авто-отправка выключена!"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Запустить авто-отправку 🚀', callback_data='enable_autosend'))
            keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, text=autosend_message,
                                    parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)


    elif button_text == 'refresh_autosend':
        # Получение времени последнего нажатия кнопки
        last_press_time = last_button_press.get(callback_query.from_user.id, 0)
        # Проверка, прошла ли секунда с момента последнего нажатия
        if time.time() - last_press_time < 1.5:
            # Если прошла менее секунды, отправляем уведомление о задержке
            await bot.answer_callback_query(callback_query.id, text="❌ Упс... Данные ещё не обновились!")
            return

        autosend, message_count, message_auto = await read_autosend()
        last_of_messages = await read_new_value()

        if autosend == "True":
            autosend_message = f"❇️ Авто-отправка запущена!\n\n🧭 Заданное количество сообщений: {message_count}\n⛽️ Заданный текст: {message_auto}\n🪂 Осталось сообщений: {last_of_messages}"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_autosend'))
            keyboard.add(types.InlineKeyboardButton(text='Выключить ❌️', callback_data='decline'))
        elif autosend == "False":
            autosend_message = "💢 Авто-отправка выключена!"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Запустить авто-отправку 🚀', callback_data='enable_autosend'))
            keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))

        # Обновляем время последнего нажатия кнопки
        last_button_press[callback_query.from_user.id] = time.time()
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, text=autosend_message,
                                    parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

    # Обработчик действия для кнопки "Запустить авто-отправку"
    elif button_text == 'enable_autosend':
        enable_autosend = "📢 Введите текст сообщения и количество сообщений с помощью кнопок:"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Выбрать количество 🧮', callback_data='select_count'))
        keyboard.add(types.InlineKeyboardButton(text='Выбрать содержание 📔', callback_data='select_content'))
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='refresh_autosend'))
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, text=enable_autosend,
                                    parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

    # Обработчик действия для кнопки "Выбрать содержание"
    elif button_text == 'select_content':
        content_message = "📔 Введите содержание сообщения:"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='decline'))
        await UserInput.message_auto.set()  # Установка состояния UserInput.message_auto
        await state.update_data(keyboard=keyboard)  # Сохранение значения keyboard в состояние
        message = await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                              message_id=callback_query.message.message_id, text=content_message,
                                              parse_mode="Markdown", reply_markup=keyboard,
                                              disable_web_page_preview=True)
        await state.update_data(
            original_message_id=message.message_id)  # Сохранение идентификатора сообщения в состояние

    # Обработчик действия для кнопки "Выбрать количество"
    elif button_text == 'select_count':
        content_message = "🧮 Введите количество сообщений:"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='decline'))
        await UserInput.message_count.set()  # Установка состояния UserInput.message_count
        await state.update_data(keyboard=keyboard)  # Сохранение значения keyboard в состояние
        message = await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                              message_id=callback_query.message.message_id, text=content_message,
                                              parse_mode="Markdown", reply_markup=keyboard,
                                              disable_web_page_preview=True)
        await state.update_data(
            original_message_id=message.message_id)  # Сохранение идентификатора сообщения в состояние

    # Обработчик действия для кнопки "Подтвердить"
    elif callback_query.data == 'confirm':
        autosend = True

        _, _, sent_messages = await read_settings()
        _, message_count, message_auto = await read_autosend()

        specified_number_messages = int(sent_messages) + int(message_count)

        await write_message_content()
        await write_remaining_messages(specified_number_messages)
        await write_autosend_content(message_auto)
        await write_autosend(autosend)

        last_of_messages = await read_new_value()
        autosend_message = f"❇️ Авто-отправка запущена!\n\n🧭 Заданное количество сообщений: {message_count}\n⛽️ Заданный текст: {message_auto}\n🪂 Осталось сообщений: {last_of_messages}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Обновить 🔄️', callback_data='refresh_autosend'))
        keyboard.add(types.InlineKeyboardButton(text='Выключить ❌️', callback_data='decline'))

        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=autosend_message, parse_mode="Markdown", reply_markup=keyboard)

    # Обработчик действия для кнопки "Отменить"
    elif callback_query.data == 'decline':
        autosend = False
        message_auto = None
        message_count = 0
        await write_residual()
        await write_autosend(autosend)
        await write_autosend_content(message_auto)
        await write_autosend_count(message_count)
        autosend_message = "💢 Авто-отправка выключена!"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Запустить авто-отправку 🚀', callback_data='enable_autosend'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, text=autosend_message,
                                    parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

    elif button_text == 'done':
        await bot.answer_callback_query(callback_query.id, text="Задача была выполнена успешно! ✔ ️")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)  # Удаление сообщения

    elif button_text == 'back':
        await bot.answer_callback_query(callback_query.id, text="Вы успешно вышли! 🎊")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)  # Удаление сообщения

        await state.finish()  # Завершение состояния

@dp.message_handler(state=UserInput.message)
async def update_message(message: types.Message, state: FSMContext):
    # Обновление сообщения
    with open('head/values/message.txt', 'w', encoding='utf-8-sig') as file:
        file.write(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()  # Завершение состояния

    # Уведомление об изменении сообщения
    await bot.send_message(chat_id=message.chat.id, text=f"✉️ Сообщение изменено на: {message.text}")

@dp.message_handler(state=UserInput.username)
async def update_username(message: types.Message, state: FSMContext):
    # Обновление имени пользователя
    with open('head/values/username.txt', 'w', encoding='utf-8-sig') as file:
        file.write(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()  # Завершение состояния

    # Уведомление об изменении имени пользователя
    await bot.send_message(chat_id=message.chat.id, text=f"👁️ Имя пользователя изменено на: {message.text}")


@dp.callback_query_handler(lambda query: query.data == 'decline', state=UserInput.message_auto)
async def cancel_message_input(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    autosend = False
    message_auto = None
    message_count = 0
    await write_autosend(autosend)
    await write_autosend_content(message_auto)
    await write_autosend_count(message_count)
    autosend_message = "💢 Авто-отправка выключена!"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Запустить авто-отправку 🚀', callback_data='enable_autosend'))
    keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=autosend_message, parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

@dp.callback_query_handler(lambda query: query.data == 'decline', state=UserInput.message_count)
async def cancel_message_input(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    autosend = False
    message_auto = None
    message_count = 0
    await write_autosend(autosend)
    await write_autosend_content(message_auto)
    await write_autosend_count(message_count)
    autosend_message = "💢 Авто-отправка выключена!"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Запустить авто-отправку 🚀', callback_data='enable_autosend'))
    keyboard.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=autosend_message, parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)


@dp.message_handler(state=UserInput.message_auto)
async def update_message(message: types.Message, state: FSMContext):
    # Получение сохраненного идентификатора сообщения
    data = await state.get_data()
    original_message_id = data.get('original_message_id')

    # Обновление сообщения пользователя
    with open('head/values/autosend_data.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    lines[0] = f"message_auto=={message.text}\n"
    with open('head/values/autosend_data.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()
    autosend, message_count, message_auto = await read_autosend()
    if message_count != "0":
        content_autosend = f"*🧭 Заданное количество сообщений:* {message_count}\n⛽️ *Заданный текст:* {message.text}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Подтвердить ❇️', callback_data='confirm'))
        keyboard.add(types.InlineKeyboardButton(text='Отменить ⛔', callback_data='decline'))
    else:
        content_autosend = f"🧭 Нужно ввести количество сообщений!\n⛽️ *Заданный текст:* {message.text}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Ввести количество 🧮', callback_data='select_count'))
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='decline'))
    # Изменение сообщения пользователя с помощью bot.edit_message_text
    await bot.edit_message_text(chat_id=message.chat.id, message_id=original_message_id, text=content_autosend, parse_mode="Markdown", reply_markup=keyboard)

@dp.message_handler(state=UserInput.message_count)
async def update_message(message: types.Message, state: FSMContext):
    # Проверка, является ли введенное сообщение числом
    if not message.text.isdigit():
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.answer_callback_query(callback_query_id=message.message_id, text="Нужно вводить только число! ☠️")
        return

    # Получение сохраненного идентификатора сообщения
    data = await state.get_data()
    original_message_id = data.get('original_message_id')

    # Обновление сообщения пользователя
    with open('head/values/autosend_data.txt', 'r') as file:
        lines = file.readlines()
    lines[1] = f"message_count=={message.text}\n"
    with open('head/values/autosend_data.txt', 'w') as file:
        file.writelines(lines)

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()

    autosend, message_count, message_auto = await read_autosend()
    if message_auto != "None":
        count_autosend = f"*🧭 Заданное количество сообщений:* {message.text}\n⛽️ *Заданный текст:* {message_auto}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Подтвердить ❇️', callback_data='confirm'))
        keyboard.add(types.InlineKeyboardButton(text='Отменить ⛔', callback_data='decline'))
    else:
        count_autosend = f"🧭 Заданное количество сообщений: {message.text}\n⛽️ Нужно ввести содержание!"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Ввести содержание 📔', callback_data='select_content'))
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='decline'))
    # Изменение сообщения пользователя с помощью bot.edit_message_text
    await bot.edit_message_text(chat_id=message.chat.id, message_id=original_message_id, text=count_autosend, parse_mode="Markdown", reply_markup=keyboard)


async def main():
    # Запуск бота
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())