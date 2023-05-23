import asyncio
import subprocess
import aiohttp
import time
import os

async def initialize_settings():
    lines = [
        "Pause==False\n",
        "formatted_time==0 часов, 0 минут, 0 секунд\n",
        "stop_count==0\n",
        "sent_messages==0\n",
        "flood_wait==0\n"
    ]
    with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)

async def clear_logs():
    with open('head/values/logs.txt', 'w', encoding='utf-8') as file:
        file.truncate(0)


async def main():
    # Выполнить инициализацию настроек и очистку логов только один раз
    await clear_logs()
    await initialize_settings()

    # Запуск файла la_start.py в отдельном процессе
    la_start_process = subprocess.Popen(['python', 'head/la_start.py'])

    # Запуск файла la_bot.py в отдельном процессе
    la_bot_process = subprocess.Popen(['python', 'head/la_bot.py'])

    try:
        # Ожидание завершения процессов при получении KeyboardInterrupt
        la_start_process.wait()
        la_bot_process.wait()
    except KeyboardInterrupt:
        # Прерывание выполнения процессов при получении KeyboardInterrupt
        la_start_process.terminate()
        la_bot_process.terminate()

    while True:
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        flood_wait = int(lines[4].split("==")[1].strip())

        while flood_wait > 0:
            flood_wait -= 1
            lines[4] = f"flood_wait=={flood_wait}\n"
            with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
                file.writelines(lines)
            time.sleep(1)

        # Проверка на изменение значения flood_wait
        new_flood_wait = int(lines[4].split("==")[1].strip())
        if new_flood_wait > 0:
            continue

        time.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
