import la_start

channel_link = 'http://t.me/+H58YW2chmh45YmNi'
limit = 2  # Максимальное количество сообщений для получения

async def read_channel_messages(channel_link, limit):
    entity = await client.get_entity(channel_link)

    last_message_id = 0  # Идентификатор последнего обработанного сообщения

    @client.on(events.NewMessage(chats=entity))
    async def message_handler(event):
        nonlocal last_message_id

        message = event.message

        if hasattr(message, 'message'):
            message_content = message.message

            if message_content.lower() == 'Босс лист':
                return  # Пропуск записи в файл для сообщений с текстом "Босс лист" или "босс лист"

            message_content = re.sub('⏳️', '', message_content)  # Удаление песочных часов из строки
            message_content = re.sub('⏳\s*Список таймеров боссов:\n*', '', message_content)  # Удаление строки "Список таймеров боссов"
            message_content = re.sub('^\d+\.\s*', '', message_content, flags=re.MULTILINE)  # Удаление цифр и точки перед каждым элементом списка
            message_content = re.sub('\s*—\s*', ' — ', message_content)  # Замена разделителя на " — "

            with open("head/values/farm_messages.txt", "a", encoding="utf-8") as file:
                file.write(message_content.strip() + "\n")  # Очищение строки от пробелов и запись в файл

            last_message_id = message.id  # Обновление идентификатора последнего обработанного сообщения

    await client.run_until_disconnected()

while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_channel_messages(channel_link, limit))
