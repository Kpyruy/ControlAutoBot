import logging
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.sync import TelegramClient
import random
import time

API_ID = '28030129'
API_HASH = '66332b905574810cfe865714c2cd743d'

client = TelegramClient('anon', API_ID, API_HASH)

async def send_message(message, username):
    entity = await client.get_input_entity(username)
    await asyncio.sleep(random.uniform(1.0, 1.3))
    try:
        await client.send_message(entity, message)
    except FloodWaitError as e:
        print(f"Waiting for {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
    except Exception as ex:
        print(f"Error: {ex}")

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
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            status = file.readline().strip()  # Читаем только первую строку
        return status == 'Pause==False'

    resumed = False

    async def update_settings(formatted_time, stop_count, sent_messages):
        lines = []
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        lines[1] = f"formatted_time=={formatted_time}\n"
        lines[2] = f"stop_count=={stop_count}\n"
        lines[3] = f"sent_messages=={sent_messages}\n"
        with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)


    while True:
        try:
            loop = asyncio.get_event_loop()

            if check_status():
                if not resumed:
                    if sent_messages > 0:
                        print("Отправка сообщений возобновлена.")
                    resumed = True
                message, username = loop.run_until_complete(read_values_from_files())
                loop.run_until_complete(send_message(message, username))
                sent_messages += 1
            else:
                if resumed:
                    print("Отправка сообщений приостановлена.")
                    resumed = False
        except KeyboardInterrupt:
            print(f"Программа была остановлена пользователем. Отправлено сообщений: {sent_messages}")
            break
        except Exception as ex:
            print(f"Error: {ex}")

        elapsed_time = time.time() - start_time
        if elapsed_time >= 750:
            stop_count += 1
            print(f"Прошло 12,5 минут. Бот приостанавливает отправку сообщений на 2,5 минуты.")
            print(f"Остановка #{stop_count} в {time.strftime('%H:%M:%S', time.localtime())}")
            time.sleep(150)
            print(f"Возобновление работы бота в {time.strftime('%H:%M:%S', time.localtime())}")
            start_time = time.time()
            resumed = False

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