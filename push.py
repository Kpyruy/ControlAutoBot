import asyncio
import subprocess
import aiohttp

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

    # Запуск файла flood_update.py в отдельном процессе
    flood_update_process = subprocess.Popen(['python', 'head/flood_update.py'])

    try:
        # Ожидание завершения процессов при получении KeyboardInterrupt
        la_start_process.wait()
        la_bot_process.wait()
        flood_update_process.wait()
    except KeyboardInterrupt:
        # Прерывание выполнения процессов при получении KeyboardInterrupt
        la_start_process.terminate()
        la_bot_process.terminate()
        flood_update_process.terminate()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())