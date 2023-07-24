from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ChatPermissions, Message
from pyrogram.raw import functions
import re
import time
import math
from datetime import date, datetime
from time import sleep
import random
import asyncio
from langdetect import detect
import wikipediaapi
import wikipedia
import fasttext
from collections import defaultdict
from translate import Translator
import pytz
import requests
from geopy.geocoders import Nominatim
from timezonefinderL import TimezoneFinder
import arrow
from translate import Translator

import locale


# API ключ OpenWeatherMap
OpenWeather_KEY = "242106ba69b46e2a5bc4badfcae321ac"

api_id = 20096642
api_hash = "cc4d7960b1288548196c28045c79539d"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Load the pre-trained language identificatiоn model
fasttext_model = fasttext.load_model("model/lid.176.bin")

# Function to detect language using Fasttext
def detect_language(text):
    predictions = fasttext_model.predict(text)
    return predictions[0][0].replace("__label__", "")

# Функция поиска в Википедии
@app.on_message(filters.command(["wiki"], prefixes=".") & filters.me)
async def wiki(_, msg):
    command = msg.text.split(".wiki ", maxsplit=1)[1]
    query = command
    language = None  # Язык по умолчанию будет определен автоматически

    query_parts = query.split(" ")
    for part in query_parts:
        if part.lower() in ["uk", "ru", "en"]:
            language = part.lower()
            query_parts.remove(part)
            query = " ".join(query_parts)
            break

    if language is None:
        # Определяем язык запроса
        detected_language = detect_language(query)
        if detected_language == "ru":
            language = "ru"
        elif detected_language == "uk":
            language = "uk"
        else:
            language = "en"

    try:
        wiki_wiki = wikipediaapi.Wikipedia(language)

        page_py = wiki_wiki.page(query)

        if page_py.exists():
            page_title = page_py.title
            page_url = page_py.fullurl
            summary = page_py.summary[0:550]  # Ограничиваем описание до 500 символов

            if language == "ru":
                response = f"**📚 Результаты поиска в Википедии для `{query}` на русском языке:**\n\n" \
                           f"**Заголовок:** {page_title}\n\n" \
                           f"**Ссылка:** {page_url}\n\n" \
                           f"**<emoji id=5447410659077661506>🌐</emoji>  Статья:**\n{summary}"
            elif language == "uk":
                response = f"**📚 Результати пошуку в Вікіпедії для `{query}` українською мовою:**\n\n" \
                           f"**Заголовок:** {page_title}\n\n" \
                           f"**Посилання:** {page_url}\n\n" \
                           f"**<emoji id=5447410659077661506>🌐</emoji>  Стаття:**\n{summary}"
            else:
                response = f"**📚 Wikipedia search results for `{query}` in English:**\n\n" \
                           f"**Title:** {page_title}\n\n" \
                           f"**Link:** {page_url}\n\n" \
                           f"**<emoji id=5447410659077661506>🌐</emoji>  Summary:**\n{summary}"
        else:
            # Если страница не найдена, попробуйте выполнить поиск с использованием точного запроса
            wikipedia.set_lang(language)
            search_results = wikipedia.search(query)

            if len(search_results) > 0:
                page = search_results[0]
                page_py = wiki_wiki.page(page)

                page_title = page_py.title
                page_url = page_py.fullurl
                summary = page_py.summary[0:500]  # Ограничиваем описание до 500 символов

                if language == "ru":
                    response = f"**📚 Результаты поиска в Википедии для `{query}` на русском языке:**\n\n" \
                               f"**Заголовок:** {page_title}\n\n" \
                               f"**Ссылка:** {page_url}\n\n" \
                               f"**<emoji id=5447410659077661506>🌐</emoji>  Статья:**\n{summary}"
                elif language == "uk":
                    response = f"**📚 Результати пошуку в Вікіпедії для `{query}` українською мовою:**\n\n" \
                               f"**Заголовок:** {page_title}\n\n" \
                               f"**Посилання:** {page_url}\n\n" \
                               f"**<emoji id=5447410659077661506>🌐</emoji>  Стаття:**\n{summary}"
                else:
                    response = f"**📚 Wikipedia search results for `{query}` in English:**\n\n" \
                               f"**Title:** {page_title}\n\n" \
                               f"**Link:** {page_url}\n\n" \
                               f"**<emoji id=5447410659077661506>🌐</emoji>  Summary:**\n{summary}"
            else:
                response = f"<emoji id=5210952531676504517>❌</emoji> No results found in Wikipedia for `{query}` in {language.upper()}."

        await msg.edit(response)
    except Exception as e:
        await msg.edit(f"<emoji id=5210952531676504517>❌</emoji> An error occurred while searching Wikipedia:\n{e}")

# Function for text translation
@app.on_message(filters.command(["tr", "t"], prefixes=".") & filters.me)
async def translate(_, msg):
    command = msg.command
    if len(command) > 2:
        text = " ".join(command[1:-1])
        target_language = command[-1].lower()
    else:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Invalid command format. Please use `.tr (text) (target_language)` or `.t (text) (target_language)`.\n\n See all target_language use: `.langcodes`")
        return

    try:
        # Detect the language of the text
        detected_language = detect_language(text)

        # Translate the text
        translator = Translator(to_lang=target_language, from_lang=detected_language)
        translation = translator.translate(text)

        if command[0] == "tr":
            await msg.edit(f"🌐 **Translation:**\n\n**<emoji id=5433811242135331842>📥</emoji> Input:** {text}\n**<emoji id=5406631276042002796>📨</emoji> Output:** {translation}")
        else:
            await msg.edit(translation)
    except Exception as e:
        await msg.edit(f"<emoji id=5210952531676504517>❌</emoji> An error occurred during translation:\n{e}")

# Function to display language codes/names
@app.on_message(filters.command("langcodes", prefixes=".") & filters.me)
async def show_language_codes(_, msg):
    language_codes = {
        "`af`": "Afrikaans",
        "`sq`": "Albanian",
        "`am`": "Amharic",
        "`ar`": "Arabic",
        "`hy`": "Armenian",
        "`az`": "Azerbaijani",
        "`eu`": "Basque",
        "`be`": "Belarusian",
        "`bn`": "Bengali",
        "`bs`": "Bosnian",
        "`bg`": "Bulgarian",
        "`ca`": "Catalan",
        "`ceb`": "Cebuano",
        "`ny`": "Chichewa",
        "`zh-cn`": "Chinese (Simplified)",
        "`zh-tw`": "Chinese (Traditional)",
        "`co`": "Corsican",
        "`hr`": "Croatian",
        "`cs`": "Czech",
        "`da`": "Danish",
        "`nl`": "Dutch",
        "`en`": "English",
        "`eo`": "Esperanto",
        "`et`": "Estonian",
        "`tl`": "Filipino",
        "`fi`": "Finnish",
        "`fr`": "French",
        "`fy`": "Frisian",
        "`gl`": "Galician",
        "`ka`": "Georgian",
        "`de`": "German",
        "`el`": "Greek",
        "`gu`": "Gujarati",
        "`ha`": "Hausa",
        "`haw`": "Hawaiian",
        "`iw`": "Hebrew",
        "`hi`": "Hindi",
        "`hmn`": "Hmong",
        "`hu`": "Hungarian",
        "`is`": "Icelandic",
        "`ig`": "Igbo",
        "`id`": "Indonesian",
        "`ga`": "Irish",
        "`it`": "Italian",
        "`ja`": "Japanese",
        "`jw`": "Javanese",
        "`kn`": "Kannada",
        "`kk`": "Kazakh",
        "`km`": "Khmer",
        "`ko`": "Korean",
        "`ku`": "Kurdish (Kurmanji)",
        "`ky`": "Kyrgyz",
        "`lo`": "Lao",
        "`la`": "Latin",
        "`lv`": "Latvian",
        "`lt`": "Lithuanian",
        "`lb`": "Luxembourgish",
        "`mk`": "Macedonian",
        "`mg`": "Malagasy",
        "`ms`": "Malay",
        "`ml`": "Malayalam",
        "`mt`": "Maltese",
        "`mi`": "Maori",
        "`mr`": "Marathi",
        "`mn`": "Mongolian",
        "`my`": "Myanmar (Burmese)",
        "`ne`": "Nepali",
        "`no`": "Norwegian",
        "`ps`": "Pashto",
        "`fa`": "Persian",
        "`pl`": "Polish",
        "`pt`": "Portuguese",
        "`pa`": "Punjabi",
        "`ro`": "Romanian",
        "`ru`": "Russian",
        "`sm`": "Samoan",
        "`gd`": "Scots Gaelic",
        "`sr`": "Serbian",
        "`st`": "Sesotho",
        "`sn`": "Shona",
        "`sd`": "Sindhi",
        "`si`": "Sinhala",
        "`sk`": "Slovak",
        "`sl`": "Slovenian",
        "`so`": "Somali",
        "`es`": "Spanish",
        "`su`": "Sundanese",
        "`sw`": "Swahili",
        "`sv`": "Swedish",
        "`tg`": "Tajik",
        "`ta`": "Tamil",
        "`te`": "Telugu",
        "`th`": "Thai",
        "`tr`": "Turkish",
        "`uk`": "Ukrainian",
        "`ur`": "Urdu",
        "`ug`": "Uyghur",
        "`uz`": "Uzbek",
        "`vi`": "Vietnamese",
    }

    language_list = "\n".join(f"{code} = {name}" for code, name in language_codes.items())
    await msg.edit(f"🌍 **Language Codes**\n\n{language_list}")

# Command to calculate the required quantity of plasma
@app.on_message(filters.command("gqp", prefixes=".") & filters.me)
async def get_quantity_of_plasma(_, msg):
    command = msg.command
    if len(command) == 3:
        current_level = int(command[1])
        desired_level = int(command[2])

        if current_level < 1 or desired_level < 1:
            await msg.edit("<emoji id=5210952531676504517>❌</emoji> Invalid input. The current and desired levels must be positive integers.")
            return

        if desired_level <= current_level:
            await msg.edit("<emoji id=5210952531676504517>❌</emoji> Invalid input. The desired level must be greater than the current level.")
            return

        plasma_cost = sum(10000 + 5000 * (level - 1) for level in range(current_level, desired_level))

        formatted_plasma_cost = "{:,}".format(plasma_cost).replace(",", " ")
        await msg.edit(f"<emoji id=5424972470023104089>🔥</emoji> **Plasma Quantity Calculation**\n\n**<emoji id=5382322671679708881>1️⃣</emoji> Current Level:** {current_level}\n**<emoji id=5381990043642502553>2️⃣</emoji> Desired Level:** {desired_level}\n\n**<emoji id=5366531532926231383>😨</emoji> Required Plasma Quantity:** {formatted_plasma_cost}")
    else:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Invalid command format. Please use `.gqp (current_level) (desired_level)`.")

# Function to calculate the remaining days until the specified month
def calculate_remaining_days(month, day=None):
    now = datetime.datetime.now()
    target_month = datetime.datetime.strptime(month, "%B").month
    target_year = now.year if target_month >= now.month else now.year + 1

    if day:
        target_date = datetime.datetime(target_year, target_month, day)
    else:
        last_day_of_month = datetime.date(target_year, target_month + 1, 1) - datetime.timedelta(days=1)
        target_date = datetime.datetime(target_year, target_month, last_day_of_month.day)

    remaining_days = (target_date - now).days

    return remaining_days

# Function to generate a progress bar based on the remaining days
def generate_progress_bar(remaining_days):
    total_days = 365
    completed_percentage = (total_days - remaining_days) / total_days
    completed_blocks = min(int(completed_percentage * 10), 10)
    empty_blocks = 10 - completed_blocks

    progress_bar = "🟩" * completed_blocks + "⬜️" * empty_blocks

    return progress_bar

# Command to calculate the remaining days until a specified month
@app.on_message(filters.command("st", prefixes=".") & filters.me)
async def remaining_days(_, msg):
    command = msg.command
    if len(command) >= 2:
        month = command[1]
        day = None

        if len(command) >= 3:
            try:
                day = int(command[2])
            except ValueError:
                pass

        remaining_days = calculate_remaining_days(month, day)
        progress_bar = generate_progress_bar(remaining_days)

        if day:
            await msg.edit(f"📅 **Countdown to {month} {day}**\n\nRemaining Days: {remaining_days}\n\n{progress_bar}")
        else:
            await msg.edit(f"📅 **Countdown to {month}**\n\nRemaining Days: {remaining_days}\n\n{progress_bar}")
    else:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Invalid command format. Please use `.st (month) [day]`.")

@app.on_message(filters.command("desc", prefixes=".") & filters.me)
async def change_description(_, msg):
    new_description = msg.text.split(maxsplit=1)[1]  # Получаем новое описание из команды
    chat_id = msg.chat.id  # Получаем ID (чата/группы/канала)

    try:
        chat = await app.get_chat(chat_id)  # Получаем информацию о чате
        if chat.permissions.can_change_info:
            await app.set_chat_description(chat_id, new_description)  # Изменяем описание
            await msg.edit(f"**Описание успешно изменено на:**\n{new_description}")
        else:
            await msg.edit("**У вас нет прав на изменение описания в этом чате**")
    except Exception as e:
        await msg.edit(f"**Произошла ошибка при изменении описания:** {str(e)}")

@app.on_message(filters.command(["ping", "p"], prefixes=".") & filters.me)
async def ping(_, msg):
    start_time = time.time()
    message = await msg.edit("<emoji id=6325806796246091512>😁</emoji> Ждем-с...")
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    await message.edit(f"**<emoji id=5215444784000277441>⚡️</emoji> Задержка между откликом:** {latency:.2f} ms")

@app.on_message(filters.command(["type", "t"], prefixes=".") & filters.me)
async def type(_, msg):
    command = msg.command
    if len(command) > 1:
        orig_text = msg.text.split(".type ", maxsplit=1)[1]
    else:
        orig_text = msg.text.split(".t ", maxsplit=1)[1]
    text = orig_text
    tbp = ""  # to be printed
    typing_symbol = "▒"

    while tbp != orig_text:
        try:
            await msg.edit(tbp + typing_symbol)
            await asyncio.sleep(0.05)  # 50 ms

            tbp = tbp + text[0]
            text = text[1:]

            await msg.edit(tbp)
            await asyncio.sleep(0.05)

        except FloodWait as e:

            await asyncio.sleep(e.x)

# Функция для получения всех айди пользователей в чате и записи их в файл
async def get_chat_user_ids(chat):
    members = []
    async for member in app.get_chat_members(chat.id):
        if member.user and not member.user.is_bot:
            members.append(str(member.user.id))
    return members

# Команда для получения и записи айди пользователей и отправки файла с айди в группу
@app.on_message(filters.command(["getids"], prefixes=".") & filters.me)
async def get_ids(_, msg):
    chat = msg.chat
    user_ids = await get_chat_user_ids(chat)

    if user_ids:
        # Записываем айди пользователей в файл
        with open("head/value/user_ids.txt", "w") as file:
            file.write(" ".join(user_ids))

        # Отправляем файл с айди пользователей в чат/группу
        await app.send_document(chat.id, "head/value/user_ids.txt", caption="User IDs in the chat:")

        await msg.edit("User IDs collected and sent.")
    else:
        await msg.edit("No user IDs found in the chat.")

# Функция для извлечения айди из текста
def extract_user_ids(text):
    pattern = r"\((\d+)\)"
    return re.findall(pattern, text)

# Команда для обработки текстового сообщения и отправки айди в другой чат
@app.on_message(filters.command(["ids"], prefixes=".") & filters.me)
async def extract_and_send_ids(_, msg):
    # Получаем текст сообщения
    text = msg.text

    # Извлекаем айди из текста
    user_ids = extract_user_ids(text)

    if user_ids:
        # Отправляем айди в другой чат (в данном случае - в текущий чат)
        await msg.reply("\n".join(user_ids))

        await msg.edit("User IDs extracted and sent.")
    else:
        await msg.edit("No user IDs found in the message.")

# Команда для сравнения айди из двух файлов и записи отсутствующих айди в текущий чат
@app.on_message(filters.command(["sum"], prefixes=".") & filters.me)
async def compare_and_send_ids(_, msg):
    # Пути к файлам с айди
    file_path1 = "head/value/user_ids.txt"
    file_path2 = "haed/value/ids.txt"

    # Читаем содержимое файлов
    with open(file_path1, "r") as file1, open(file_path2, "r") as file2:
        ids1 = set(file1.read().strip().split())
        ids2 = set(file2.read().strip().split())

    # Находим отсутствующие айди из user_ids в ids
    missing_ids = ids2.difference(ids1)

    if missing_ids:
        # Отправляем отсутствующие айди в текущий чат
        message = "Missing IDs in user_ids:\n" + "\n".join(missing_ids)
        await msg.edit(message)
    else:
        await msg.edit("No missing IDs found.")

@app.on_message(filters.command("calc", prefixes=".") & filters.me)
async def calc(_, msg):
    command_parts = msg.text.split(".calc ", maxsplit=1)
    if len(command_parts) < 2:
        await msg.edit(
            "<emoji id=5220149804708930165>📈</emoji> Введите выражение для вычисления.\n\n"
            "**Логарифм:**\n"
            "Натуральный логарифм числа 10: `log(10)`\n"
            "Логарифм числа 100 по основанию 10: `log(100, 10)`\n\n"
            "**Корень:**\n"
            "Квадратный корень из числа 16: `sqrt(16)`\n"
            "Кубический корень из числа 27: `pow(27, 1/3)`\n\n"
            "**Степень:**\n"
            "Квадрат числа 5: `pow(5, 2)`\n"
            "Куб числа 3: `pow(3, 3)`\n"
            "Число 10 возводится в 5 степень: `10 ** 5`"

        )
        return

    expression = command_parts[1]

    # Замена формата sqrt на math.sqrt и log на math.log
    expression = expression.replace("sqrt", "math.sqrt")
    expression = expression.replace("log", "math.log")

    try:
        result = eval(expression)

        result_str = str(result)
        if isinstance(result, (int, float)) and abs(result) > 1e6:
            with open("head/value/calc_result.txt", "w") as file:
                file.write(result_str)
            await msg.edit(
                f"<emoji id=5440660757194744323>‼️</emoji> Результат слишком большой.\n\n<emoji id=5980787993139481991>🔺</emoji> Запрос: `{expression}`\n\n📄 Отправляю текстовый файл с ответом:"
            )
            await msg.reply_document("head/value/calc_result.txt")
        else:
            await msg.edit(
                f"<emoji id=5980787993139481991>🔺</emoji> Запрос: `{expression}`\n\n<emoji id=5231200819986047254>📊</emoji> Результат: `{result_str}`"
            )

    except SyntaxError:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Неправильный синтаксис выражения.")
    except ZeroDivisionError:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Деление на ноль недопустимо.")
    except OverflowError:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Результат слишком большой для вычисления.")
    except Exception as e:
        await msg.edit(f"<emoji id=5210952531676504517>❌</emoji> Произошла ошибка при вычислении выражения:\n{e}")

# Function to get a random quote from Quotable API
def get_random_quote():
    response = requests.get("https://api.quotable.io/random")
    if response.status_code == 200:
        data = response.json()
        content = data["content"]
        author = data["author"]
        return f"{content} - {author}"
    else:
        return "Failed to fetch a random quote."

# Function for text translation
def translate_text(text, target_language):
    translator = Translator(to_lang=target_language)
    translation = translator.translate(text)
    return translation

# Command for random quotes with translation
@app.on_message(filters.command("quote", prefixes=".") & filters.me)
async def random_quote(_, msg):
    command = msg.command
    target_language = None

    if len(command) > 1:
        target_language = command[1].lower()

    quote = get_random_quote()

    if target_language:
        translated_quote = translate_text(quote, target_language)
        await msg.edit(f"**<emoji id=5465143921912846619>💭</emoji> Original Quote:**\n\n{quote}\n\n**<emoji id=5465143921912846619>💭</emoji> Translated Quote ({target_language}):**\n\n{translated_quote}")
    else:
        await msg.edit(f"{quote}")

# Словарь с соответствиями погоды и эмодзи
weather_emojis = {
    "Clear": "<emoji id=5458842406025699616>☀️</emoji>",
    "Clouds": "<emoji id=5456176829062717080>☁️</emoji>",
    "Drizzle": "<emoji id=5458859474225734343>🌦</emoji>",
    "Rain": "<emoji id=5283243028905994049>🌧</emoji>",
    "Thunderstorm": "<emoji id=5458498331900650796>⛈</emoji>",
    "Snow": "<emoji id=5458590407409541785>🌨</emoji>",
    "Mist": "<emoji id=5456289438810251585>🌧</emoji>",
    "Haze": "<emoji id=5456289438810251585>🌧</emoji>",
    "Fog": "<emoji id=5458849741829842481>☁️</emoji>",
    "Smoke": "<emoji id=5458849741829842481>☁️</emoji>",
    "Sand": "<emoji id=5458710988616375939>⏳</emoji>",
    "Squall": "<emoji id=5458747839435776472>🌬</emoji>",
    "Tornado": "<emoji id=5458813457946125655>🌪</emoji>",
    "Ash": "🌋"
}

def get_weather(city):
    try:
        # Формирование URL запроса к OpenWeatherMap API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OpenWeather_KEY}&units=metric"

        # Отправка запроса и получение данных в формате JSON
        response = requests.get(url)
        data = response.json()

        # Извлечение информации о погоде из полученных данных
        weather = data["weather"][0]["main"]
        weather_emoji = weather_emojis.get(weather, "")
        temperature = data["main"]["temp"]

        # Получение времени
        time_utc = data["dt"]

        # Геокодирование адреса города
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        latitude = location.latitude
        longitude = location.longitude

        # Определение временной зоны города и конвертация UTC времени в местное время
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
        timezone = pytz.timezone(timezone_str)
        time_local = datetime.fromtimestamp(time_utc, tz=timezone)

        # Форматирование текста с информацией о погоде
        timezone_offset = time_local.strftime(
            '%z')  # Получение значения смещения временной зоны в формате "+HHMM" или "-HHMM"
        timezone_sign = "+" if timezone_offset[0] == "+" else "-"  # Определение знака смещения временной зоны
        timezone_offset = timezone_offset[1:3].lstrip('0')  # Получение значения смещения без ведущего знака и нуля
        timezone_formatted = f"GMT {timezone_sign}{timezone_offset}"

        time_formatted = arrow.utcnow().to(timezone).format("DD.MM.YYYY HH:mm")

        if temperature >= int("0"):
            thermometer = "<emoji id=5458786979472744976>🌡</emoji>"
        else:
            thermometer = "<emoji id=5456573443522700218>🥶</emoji>"

        text = f"**📍 Location:** {city}\n\n" \
               f"**{weather_emoji} Weather:** {weather}\n" \
               f"**{thermometer} Temperature:** {temperature} °C\n" \
               f"**<emoji id=5451732530048802485>⏳</emoji> Date:** {time_formatted} {timezone_formatted}"

        return text
    except Exception as e:
        return f"<emoji id=5210952531676504517>❌</emoji> Произошла ошибка при получении погоды: {e}"

# Функция для обработки команды .w или .weather
@app.on_message(filters.command(["w", "weather"], prefixes=".") & filters.me)
async def weather(_, msg):
    command = msg.command
    if len(command) > 1:
        city = " ".join(command[1:])
        weather_info = get_weather(city)
        await msg.edit(weather_info)
    else:
        await msg.edit("<emoji id=5210952531676504517>❌</emoji> Неверный формат команды. Используйте `.w (город или страна)` или `.weather (город или страна)`.")

# Команда взлома пентагона
@app.on_message(filters.command("secret", prefixes=".") & filters.me)
async def hack(_, msg):
    # Проверка на наличие текста после команды
    if len(msg.command) > 1:
        secret_text = msg.text.split(maxsplit=1)[1]
    else:
        secret_text = "Лох"  # Текст по умолчанию, если не указан

    perc = 0

    while perc < 100:
        try:
            text = f"**<emoji id=5447644880824181073>⚠️</emoji> Загрузка секретных данных:** {perc}%..."
            await msg.edit(text)

            perc += random.randint(1, 3)
            await asyncio.sleep(0.07)

        except FloodWait as e:
            await asyncio.sleep(e.x)

    await msg.edit("**<emoji id=5206607081334906820>✔️</emoji> Данные успешно загружены!**")
    await asyncio.sleep(3)

    await msg.edit("**<emoji id=5431609822288033666>🤫</emoji> Подготовка данных...**")
    perc = 0

    while perc < 100:
        try:
            text = f"**<emoji id=5431609822288033666>🤫</emoji>  Подготовка данных:** {perc}%..."
            await msg.edit(text)

            perc += random.randint(1, 5)
            await asyncio.sleep(0.1)

        except FloodWait as e:
            await asyncio.sleep(e.x)

    await msg.edit(f"<emoji id=5397782960512444700>📌</emoji> == ||**{secret_text}**||")

afk_mode = False
afk_info = {}
answered_users = set()

@app.on_message(filters.private & filters.incoming)
async def afk_handler(_, msg):
    global afk_mode
    global afk_info
    global answered_users

    chat_id = msg.chat.id
    sender_id = msg.from_user.id

    if msg.text is not None:
        command = msg.text.lower()
    else:
        # Обработка случая, когда сообщение не содержит текста
        return

    if afk_mode and sender_id != 1738263685 and not msg.from_user.is_bot and sender_id not in answered_users:
        timestamp = afk_info["timestamp"]
        reason = afk_info["reason"]
        time_diff = datetime.datetime.now() - timestamp
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours} h, {minutes} min, {seconds} s"

        if reason:
            message = (
                f"**🏙️ I'm not here right now, so I'll answer later.**\n"
                f"**❇️ Been online:** {duration_str} ago.\n"
                f"**📝 Reason:** {reason}"
            )
        else:
            message = (
                f"**🏙️ I'm not here right now, so I'll answer later.**\n"
                f"**❇️ Been online:** {duration_str} ago.\n"
            )

        await app.send_message(chat_id, message)
        answered_users.add(sender_id)
        return

    if command.startswith(".afk"):
        if afk_mode:
            afk_mode = False
            await msg.edit("☄️ I'm back!")
            answered_users.clear()
        else:
            afk_mode = True
            afk_info["timestamp"] = datetime.now()
            reason = command[5:].strip() if len(command) > 5 else None
            afk_info["reason"] = reason

            await msg.edit("🍃 I'm leaving, turning on AFK mode")
    elif command.startswith(".check"):
        if afk_mode:
            timestamp = afk_info["timestamp"]
            reason = afk_info["reason"]
            time_diff = datetime.datetime.now()- timestamp
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours} h, {minutes} min, {seconds} s"

            if reason:
                message = (
                    f"**🏙️ I'm not here right now, so I'll answer later.**\n"
                    f"**❇️ Been online:** {duration_str} ago.\n"
                    f"**📝 Reason:** {reason}"
                )
            else:
                message = (
                    f"**🏙️ I'm not here right now, so I'll answer later.**\n"
                    f"**❇️ Been online:** {duration_str} ago.\n"
                )

            await app.send_message(chat_id, message)
        else:
            await app.send_message(chat_id, "<emoji id=5447410659077661506>🌐</emoji>  I'm available right now.")

app.run()
