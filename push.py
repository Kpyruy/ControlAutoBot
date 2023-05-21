import asyncio
import subprocess
import aiohttp
import time

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
    lines = []
    with open('head/values/settings.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)

loop = asyncio.get_event_loop()
loop.run_until_complete(clear_logs())
loop.run_until_complete(initialize_settings())

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
    with open('head/values/username.txt', 'r') as file:
        username = file.read().strip()

    with open('head/values/message.txt', 'r') as file:
        message = file.read().strip()

    time.sleep(1)
