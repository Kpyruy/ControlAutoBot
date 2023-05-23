import asyncio

async def main():
    while True:
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        flood_wait = int(lines[4].split("==")[1].strip())

        while flood_wait > 0:
            flood_wait -= 1
            lines[4] = f"flood_wait=={flood_wait}\n"
            with open('head/values/settings.txt', 'w', encoding='cp1251') as file:
                file.writelines(lines)
            await asyncio.sleep(1)

        # Проверка на изменение значения flood_wait
        with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
            new_lines = file.readlines()
        new_flood_wait = int(new_lines[4].split("==")[1].strip())
        if new_flood_wait > 0:
            continue

        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
