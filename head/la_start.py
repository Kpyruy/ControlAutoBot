import pytz
from datetime import datetime
import logging
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.sync import TelegramClient
import random
import time
import os
from configparser import ConfigParser

#API_ID = '28030129'
#API_HASH = '66332b905574810cfe865714c2cd743d'

config = ConfigParser()
config.read('private/.env')

API_ID = config.get('API', 'API_ID')
API_HASH = config.get('API', 'API_HASH')

client = TelegramClient('anon', API_ID, API_HASH)

async def get_delay():
    with open("head/values/delay.txt", "r") as file:
        delay = float(eval(file.read().strip()))
    return delay

flood_wait_active = False

async def forward_messages_in_background(entity):
    try:
        while flood_wait_active:
            await client.forward_messages(entity, 27860950, 1738263685)

            delay = await get_delay()
            await asyncio.sleep(delay)
    except Exception as e:
        write_to_logs(f"Catch some problem - {e}")


async def send_message(message, username):
    global flood_wait_active
    entity = await client.get_input_entity(username)
    delay = await get_delay()
    await asyncio.sleep(delay)
    try:
        await client.send_message(entity, message)
        flood_wait_active = False
    except FloodWaitError as e:
        flood_wait_active = True
        asyncio.create_task(forward_messages_in_background(entity))

        write_to_logs(f"Waiting for {e.seconds} seconds")
        await update_flood_wait(e.seconds)
        await asyncio.sleep(e.seconds)

    except Exception as ex:
        print(f"Error: {ex}")


async def update_flood_wait(new_value):
    with open('head/values/flood_wait.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()
    lines[0] = f"flood_wait=={new_value}\n"  # Запись нового значения flood_wait
    with open('head/values/flood_wait.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)

async def read_values_from_files():
    with open('head/values/username.txt', 'r', encoding='utf-8-sig') as file:
        username = file.read().strip()

    with open('head/values/message.txt', 'r', encoding='utf-8-sig') as file:
        message = file.read().strip()

    return message, username

with client:
    sent_messages = 0
    start_time = time.time()
    stop_count = 0
    starttime = time.time()

    # Проверка файла settings.txt для определения статуса (остановлено/возобновлено)
    def check_status():
        with open('head/values/pause.txt', 'r', encoding='cp1251') as file:
            status = file.readline().strip()  # Читаем только первую строку
        return status == 'Pause==False'

    resumed = False

    async def update_settings(formatted_time, stop_count, sent_messages):
        lines = []
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        lines[0] = f"formatted_time=={formatted_time}\n"
        lines[1] = f"stop_count=={stop_count}\n"
        lines[2] = f"sent_messages=={sent_messages}\n"
        with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)


    def write_to_logs(message):
        current_time = datetime.now(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S')
        with open('head/values/logs.txt', 'a', encoding='utf-8') as file:
            file.write(f"[{current_time}] {message}\n")

    while True:
        try:
            loop = asyncio.get_event_loop()

            if check_status():
                if not resumed:
                    if sent_messages > 0:
                        write_to_logs("Отправка сообщений возобновлена.")
                    resumed = True
                message, username = loop.run_until_complete(read_values_from_files())
                loop.run_until_complete(send_message(message, username))
                sent_messages += 1
            else:
                if resumed:
                    write_to_logs("Отправка сообщений приостановлена.")
                    resumed = False
        except KeyboardInterrupt:
            write_to_logs(f"Программа была остановлена пользователем. Отправлено сообщений: {sent_messages}")
            break
        except Exception as ex:
            write_to_logs(f"Error: {ex}")

        elapsed_time = time.time() - start_time
        if elapsed_time >= 750:
            # stop_count += 1
            # write_to_logs("Прошло 12,5 минут. Бот приостанавливает отправку сообщений на 2,5 минуты.")
            # write_to_logs(f"Остановка #{stop_count} в {time.strftime('%H:%M:%S', time.localtime())}")
            # time.sleep(150)
            # write_to_logs(f"Возобновление работы бота в {time.strftime('%H:%M:%S', time.localtime())}")
            start_time = time.time()
            # resumed = False

        total_elapsed_time = time.time() - starttime
        hours = int(total_elapsed_time // 3600)
        minutes = int((total_elapsed_time % 3600) // 60)
        seconds = int(total_elapsed_time % 60)

        hours_str = f"{hours} час"
        if hours == 0:
            hours_str += "ов"
        elif hours == 1:
            hours_str += ""
        elif 2 <= hours <= 4:
            hours_str += "a"
        elif hours >= 5:
            hours_str += "ов"

        minutes_str = f"{minutes} минут"
        if minutes == 1:
            minutes_str += "а"
        elif 2 <= minutes <= 4:
            minutes_str += "ы"
        elif minutes >= 5:
            minutes_str += ""

        seconds_str = f"{seconds} секунд"
        if seconds == 1:
            seconds_str += "а"
        elif 2 <= seconds <= 4:
            seconds_str += "ы"
        elif seconds >= 5:
            seconds_str += ""

        formatted_time = f"{hours_str}, {minutes_str}, {seconds_str}"

        loop.run_until_complete(update_settings(formatted_time, stop_count, sent_messages))
