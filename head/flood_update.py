import time
import sys

def check_flood_wait():
    try:
        while True:
            with open('head/values/flood_wait.txt', 'r', encoding='cp1251') as file:
                lines = file.readlines()

            if len(lines) >= 1:
                current_flood_wait = int(lines[0].split("==")[1].strip())

                if current_flood_wait > 0:
                    decrement_flood_wait(current_flood_wait)

            time.sleep(1)  # Период опроса файла

    except KeyboardInterrupt:
        sys.exit(0)

def decrement_flood_wait(new_value):
    with open('head/values/flood_wait.txt', 'r', encoding='cp1251') as file:
        lines = file.readlines()

    if len(lines) >= 1:
        lines[0] = f"flood_wait=={max(int(new_value) - 1, 0)}\n"  # Уменьшение значения flood_wait на 1
        with open('head/values/flood_wait.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)

        # Обновление содержимого файла
        lines = [f"flood_wait=={max(int(new_value) - 1, 0)}\n"]
        with open('head/values/flood_wait.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)

check_flood_wait()
