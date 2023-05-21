import asyncio
import subprocess
import aiohttp
import time

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