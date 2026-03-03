import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import pytz
from datetime import datetime, date, timedelta
import os
import random
from bs4 import BeautifulSoup
import threading

TOKEN = '7900558403:AAEECbhUHJSkOYwmLl2bLUP4kqFiYVgOrk8'
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.txt"

# ────────────────────────────────────────────────
#   РАСПИСАНИЕ (оставляем только то, что есть)
# ────────────────────────────────────────────────
schedule = {
    '10': {
        'monday': [
            '1. Разговоры о важном',
            '2. История',
            '3. Физ-ра',
            '4. Алгебра',
            '5. Индивидуальный проект',
            '6. Физика',
            '7. Англ. яз.'
        ],
        'tuesday': [
            '1. Русский язык',
            '2. ОБиЗР',
            '3. Алгебра',
            '4. Обществознание',
            '5. Геометрия',
            '6. История',
            '7. Литература'
        ],
        'wednesday': [
            '1. Обществознание',
            '2. Англ. яз.',
            '3. Русский язык',
            '4. Русский язык',
            '5. Информатика',
            '6. Биология',
            '7. Литература'
        ],
        'thursday': [
            '1. Обществознание',
            '2. Химия',
            '3. Физика',
            '4. Геометрия',
            '5. Геометрия',
            '6. Вероятность и статистика',
            '7. Литература'
        ],
        'friday': [
            '1. География',
            '2. Обществознание',
            '3. Физкультура',
            '4. Алгебра',
            '5. Алгебра',
            '6. Англ. яз.'
        ],
    },
}

BELLS = [
    '<b>1</b>   <u>08:30 – 09:15</u>',
    '    09:15 – 09:25  (10 мин)',
    '<b>2</b>   <u>09:25 – 10:10</u>',
    '    10:10 – 10:30  (20 мин)',
    '<b>3</b>   <u>10:30 – 11:15</u>',
    '    11:15 – 11:25  (10 мин)',
    '<b>4</b>   <u>11:25 – 12:10</u> ',
    '    12:10 – 12:20  (10 мин)',
    '<b>5</b>   <u>12:20 – 13:05</u> ',
    '    13:05 – 13:25  (20 мин)',
    '<b>6</b>   <u>13:25 – 14:10</u>',
    '    14:10 – 14:30  (20 мин)',
    '<b>7</b>   <u>14:30 – 15:15</u>',
]

MEALS = [
    'Завтрак:           <u>10:10 – 10:30</u>',
    'Обед:              <u>14:10 – 14:30</u>',
    'Полдник:           <u>15:30</u>'
]   

DAYS_RU = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье'
}

# ────────────────────────────────────────────────
#   Погода
# ────────────────────────────────────────────────
CITY_LAT = 44.95
CITY_LON = 34.10

def get_weather_text():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={CITY_LAT}&longitude={CITY_LON}"
            f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,surface_pressure"
            f"&timezone=Europe%2FMoscow"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        temp_now = current.get("temperature_2m", "?")
        feels_like = current.get("apparent_temperature", "?")
        humidity = current.get("relative_humidity_2m", "?")
        wind_speed = current.get("wind_speed_10m", "?")
        pressure = current.get("surface_pressure", "?")
        weather_code = current.get("weather_code", 0)

        weather_desc = {
            0: "Ясно ☀️", 1: "Преимущественно ясно", 2: "Малооблачно ⛅", 3: "Пасмурно ☁️",
            45: "Туман", 51: "Лёгкая морось", 61: "Небольшой дождь 🌧️", 71: "Небольшой снег ❄️",
            95: "Гроза ⚡",
        }
        condition = weather_desc.get(weather_code, f"Переменчивая погода (код {weather_code})")

        now = datetime.now(pytz.timezone("Europe/Moscow"))
        date_str = now.strftime("%d.%m.%Y")

        advice = ""
        try:
            temp = float(temp_now)
            wind = float(wind_speed)
            if temp < 5:
                advice = "Сегодня холодно ❄️ Надень шапку🤗"
            elif temp < 10:
                advice = "Прохладно, особенно утром. Шапка и шарф не помешают!"
            elif temp < 15:
                advice = "Весна, но ещё прохладно. Лучше взять шапку на всякий случай."
            else:
                advice = "Достаточно тепло ☀️ Шапку можно оставить дома."
            if wind > 10:
                advice += "\nВетер сильный — капюшон или шапка точно пригодятся!"
        except:
            advice = "Погода переменчивая. Лучше взять шапку на всякий случай."

        return (
            f"☀️ Погода в Симферополе на сегодня ({date_str})\n\n"
            f"Сейчас: **{temp_now}°C** (ощущается как {feels_like}°C)\n"
            f"{condition}\n\n"
            f"Ветер: {wind_speed} км/ч   Влажность: {humidity}%   Давление: {pressure} мм рт.ст.\n\n"
            f"**Совет:** {advice}"
        )
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "Не удалось загрузить погоду 😔 Попробуй позже"

# ────────────────────────────────────────────────
#   ФАКТЫ
# ────────────────────────────────────────────────
# Глобально где-то в начале файла (или в функции)
CURRENT_FACT_INDEX = {}  # словарь chat_id → текущий индекс факта

def get_fact_of_the_day(chat_id, next_one=False):
    try:
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        date_str = now.strftime("%Y-%m-%d")
        
        # Ключевой параметр — dates=YYYY-MM-DD
        url = (
            f"https://kudago.com/public-api/v1.4/events/"
            f"?fields=title,description,dates,age_restriction"
            f"&dates={date_str}"
            f"&order_by=-popularity"           # от самых популярных/важных
            f"&page_size=20"                    # берём побольше, чтобы было из чего выбирать
            f"&text_format=plain"
        )
        
        response = requests.get(url, timeout=7)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return "Сегодня в доступных источниках не нашлось дополнительных интересных событий 😔\nМожет, это день для твоего собственного рекорда?"

        # Управляем индексом для этого пользователя
        if chat_id not in CURRENT_FACT_INDEX:
            CURRENT_FACT_INDEX[chat_id] = 0
        
        if next_one:
            CURRENT_FACT_INDEX[chat_id] += 1
        
        idx = CURRENT_FACT_INDEX[chat_id] % len(results)  # зацикливаем, если дошли до конца
        
        event = results[idx]
        title = event.get("title", "Событие дня").strip()
        desc = event.get("description", "").strip()
        
        if len(desc) > 320:
            desc = desc[:317] + "..."
        
        date_display = now.strftime("%d.%m.%Y")
        text = f"✨ Рандомный факт:\n\n**{title}**\n\n{desc}"
        
        return text
    
    except Exception as e:
        print(f"Ошибка при получении факта: {e}")
        fallbacks = [
            f"{now.strftime('%d.%m')} — день, когда можно позволить себе чуть больше сладкого 🍫",
            "Исторический факт: в этот день кто-то где-то придумал что-то гениальное... возможно, даже ты сегодня!",
            "Сегодня хороший день для улыбки — это уже само по себе событие 😊"
        ]
        return random.choice(fallbacks)
# ────────────────────────────────────────────────
#   КАНИКУЛЫ
# ────────────────────────────────────────────────
HOLIDAYS = [
    ("Осенних 2025",   date(2025, 10, 25), date(2025, 11,  3)),
    ("Зимних 2025/2026", date(2025, 12, 27), date(2026,  1, 11)),
    ("Весенних 2026",  date(2026,  3, 28), date(2026,  4,  5)),
    ("Осенних 2026",   date(2026, 10, 24), date(2026, 11,  1)),
    ("Зимних 2026/2027", date(2026, 12, 31), date(2027,  1, 10)),
    ("Весенних 2027",  date(2027,  3, 27), date(2027,  4,  4)),
    ("Летних 2027",    date(2027,  5, 29), date(2027,  8, 31)),
]

def days_to_next_holidays():
    now = datetime.now(pytz.timezone('Europe/Moscow')).date()
    next_start = None
    holiday_name = ""
    holiday_year = ""

    for full_name, start, end in HOLIDAYS:
        if end < now:
            continue
        if now < start:
            next_start = start
            if "2026" in full_name:
                holiday_name = full_name.replace(" 2026", "")
                holiday_year = "2026"
            elif "2027" in full_name:
                holiday_name = full_name.replace(" 2027", "").replace(" 2026/2027", "")
                holiday_year = "2026/2027"
            else:
                holiday_name = full_name
            break
        elif start <= now <= end:
            return f"Сейчас идут {full_name.lower()}! 🎉 Отдыхай!"

    if next_start is None:
        return "Каникулы закончились... Но скоро новые! 🌟"

    days_left = (next_start - now).days
    when = f"({next_start.strftime('%d.%m.%Y')})" if days_left > 60 else ""

    if days_left == 0:
        return f"Сегодня начинаются {holiday_name.lower()} {holiday_year}! Урааа! 🎈"
    elif days_left == 1:
        return f"До {holiday_name.lower()} {holiday_year} остался 1 день! {when}"
    else:
        return f"До {holiday_name.lower()} {holiday_year} осталось {days_left} дней {when}"

# ────────────────────────────────────────────────
#   ГЛАВНОЕ МЕНЮ
# ────────────────────────────────────────────────
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("📚 Уроки", callback_data="menu_lessons"),
        InlineKeyboardButton("🔔 Звонки", callback_data="menu_bells")
    )
    markup.row(
        InlineKeyboardButton("🍽 Покушать", callback_data="menu_meals"),
        InlineKeyboardButton("🏖 До каникул", callback_data="menu_holidays")
    )
    markup.row(
        InlineKeyboardButton("☀️ Погода", callback_data="menu_weather"),
        InlineKeyboardButton("📜 Рус. факты", callback_data="menu_fact")
    )
    return markup

# ────────────────────────────────────────────────
#   START
# ────────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    text = (
        "Привет! 👋\n"
        "Я — твой личный помощник по расписанию школы Воронцова ✨\n\n"
        "📚 Уроки\n"
        "🔔 Звонки\n"
        "🍽️ Покушать\n\n"
        "Выбирай, что нужно сегодня! ↓\n\n"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

# ────────────────────────────────────────────────
#   CALLBACK — УРОКИ теперь сразу показывают расписание на сегодня
# ────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data

    if data == "menu_lessons":
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Показываем только будние дни (Пн–Пт)
        days = [
            ("monday", "Понедельник"),
            ("tuesday", "Вторник"),
            ("wednesday", "Среда"),
            ("thursday", "Четверг"),
            ("friday", "Пятница"),
        ]
        
        for eng, ru in days:
            markup.add(InlineKeyboardButton(ru, callback_data=f"lessons_day_{eng}"))
        
        markup.add(InlineKeyboardButton("← Главное меню", callback_data="back_main"))
        
        bot.edit_message_text(
            "Выбери день недели, расписание которого хочешь посмотреть:",
            cid, mid, reply_markup=markup
        )

    elif data.startswith("lessons_day_"):
        day_eng = data.split("_")[2]  # lessons_day_monday → monday
        day_ru = DAYS_RU.get(day_eng, day_eng.capitalize())

        # Класс по умолчанию (можно изменить на '5', '6' или сделать выбор позже)
        default_class = '10'

        if default_class not in schedule or day_eng not in schedule[default_class]:
            text = f"Расписание на {day_ru} для {default_class} класса пока не добавлено 😔"
        else:
            lessons = schedule[default_class][day_eng]
            text = f"📅 {day_ru}, {default_class} класс\n\n" + "\n".join(lessons)

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("← Другие дни", callback_data="menu_lessons"))
        markup.add(InlineKeyboardButton("← Главное меню", callback_data="back_main"))

        bot.edit_message_text(text, cid, mid, reply_markup=markup)

    elif data == "menu_bells":
        text = "🔔 Расписание звонков\n\n" + "\n".join(BELLS)
        markup = get_back_markup()
        bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode="HTML")

    elif data == "menu_meals":
        text = "🍽 Расписание питания\n\n" + "\n".join(MEALS)
        markup = get_back_markup()
        bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode="HTML")

    elif data == "menu_weather":
        text = get_weather_text()
        markup = get_back_markup()
        bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode="Markdown")

    elif data == "menu_holidays":
        text = f"🏖 **До каникул**\n\n{days_to_next_holidays()}"
        markup = get_back_markup()
        bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode="Markdown")

    elif data == "menu_fact":
        text = get_fact_of_the_day(call.message.chat.id, next_one=False)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Ещё факт 🔄", callback_data="more_fact")
        )
        markup.add(InlineKeyboardButton("← Главное меню", callback_data="back_main"))
    
        bot.edit_message_text(
            text,
            cid, mid,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "more_fact":
        text = get_fact_of_the_day(call.message.chat.id, next_one=True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Ещё факт 🔄", callback_data="more_fact")
        )
        markup.add(InlineKeyboardButton("← Главное меню", callback_data="back_main"))
    
        bot.edit_message_text(
            text,
            cid, mid,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "back_main":
        bot.edit_message_text("Что хочешь посмотреть?", cid, mid, reply_markup=get_main_menu())

def get_back_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("← Главное меню", callback_data="back_main"))
    return markup

# ────────────────────────────────────────────────
#   save_user и load_users (оставляем как было)
# ────────────────────────────────────────────────
def save_user(chat_id):
    chat_id_str = str(chat_id)
    if not os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                f.write(chat_id_str + '\n')
            print(f"Создан users.txt → добавлен {chat_id}")
            return
        except Exception as e:
            print(f"Ошибка создания файла: {e}")
            return

    existing = set()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    existing.add(stripped)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")

    if chat_id_str not in existing:
        try:
            with open(USERS_FILE, 'a', encoding='utf-8') as f:
                f.write(chat_id_str + '\n')
            print(f"Добавлен новый пользователь: {chat_id}")
        except Exception as e:
            print(f"Ошибка записи: {e}")

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    users = []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.isdigit():
                    users.append(int(stripped))
    except Exception as e:
        print(f"Ошибка загрузки users.txt: {e}")
    return users

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()