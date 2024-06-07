import subprocess
import asyncio


async def initialize_settings():
    lines = [
        "formatted_time==0 часов, 0 минут, 0 секунд\n"
        "stop_count==0\n",
        "sent_messages==0\n"
    ]
    with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)
    lines = [
        "Pause==False\n"
    ]
    with open('head/values/pause.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)
    lines = [
        "autosend==False\n"
    ]
    with open('head/values/autosend.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)
    lines = [
        "message_auto == None\n",
        "message_count == 0"
    ]
    with open('head/values/autosend_data.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)
    lines = [
        "remaining_messages==0\n"
    ]
    with open('head/values/remaining_messages.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)
    lines = [
        "new_value==0\n"
    ]
    with open('head/values/new_message_value.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)
    lines = [
        "flood_wait==0\n"
    ]
    with open('head/values/flood_wait.txt', 'w', encoding='cp1251') as file:
        file.writelines(lines)
    lines = [
        "Stop==False\n"
    ]
    with open('head/values/stop.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)
    lines = [
        "first_value==None\n"
        "second_value==None\n",
    ]
    with open('head/values/randomise.txt', 'w', encoding='utf-8') as file:
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

    # Запуск файла remaining_update.py в отдельном процессе
    remaining_process = subprocess.Popen(['python', 'head/remaining_update.py'])

    try:
        # Ожидание завершения процессов при получении KeyboardInterrupt
        la_start_process.wait()
        la_bot_process.wait()
        flood_update_process.wait()
        remaining_process.wait()

    except KeyboardInterrupt:
        # Прерывание выполнения процессов при получении KeyboardInterrupt{}
        la_start_process.terminate()
        la_bot_process.terminate()
        flood_update_process.terminate()

asyncio.run(main())
