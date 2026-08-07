import telebot
from telebot import types
import json
import os
import math

# ===== ТВОЙ ТОКЕН ОТ @BotFather =====
TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
bot = telebot.TeleBot(TOKEN)

# ===== ССЫЛКА НА ТВОЙ САЙТ =====
SITE_URL = "https://asperxyourtopsongs.netlify.app/"

# ===== СПИСОК ПЕСЕН (для рейтинга, пока не используется) =====
SONGS = [
    "Bad Trip", "Monsta", "Plague", "Sorry Not Sorry", "Über Ich",
    "Будет больно", "Был таким всегда", "В долгий путь", "Вместе",
    "Ветер перемен (2 раунд 17 независимый баттл)", "Волчок",
    "Всё разбито", "Всё, что должно умереть", "Выстрели",
    "Дело нескольких минут", "Демоны города Икс", "Держись",
    "Дрянь", "Дыхание", "Дышать и жить", "Жить", "Заряжай",
    "Земля", "Звёздная", "Змея", "Игра", "Имя", "Ищи",
    "Каждый справляется сам", "Каприз", "Карантинка",
    "Картонная", "Квадрат Декарта",
    "Классики (feat. tamagotchik)", "Колыбельная",
    "Космос", "Крики планет", "Курит и молчит",
    "Лабиринт (feat. ЛИСН)", "Линии жизни",
    "Локус генома", "Любовь и ненависть на улице Ленина",
    "Мой Бог", "Море", "Мотыльки (feat. Port Avenue)",
    "Мы не железные", "Надо улыбаться", "Не люблю",
    "Не выходи", "Не переживай", "Никому не говори",
    "От автора", "Патрон", "Пей, лечись, люби (feat. Гарри Топор)",
    "Перелом", "Петь в тишине", "Питер Пэйн",
    "План", "Почти получилось", "Праздничная",
    "Прикосновение", "Приходи ко мне (feat. МОНТГОМЕРИ)",
    "Привидения", "Прозерпина", "Приметы (feat. ГОТЭМ)",
    "Просто поговорить", "Прости (feat. VULPES VULT!)",
    "ПТСР (feat. Ctrl+Freak)", "Пускай весь мир разлетается по кускам",
    "Пустота (feat. Ctrl+Freak)", "Радость",
    "Самая честная песня", "Сгораю", "Сказка",
    "Скоро узнаешь", "Слёзы сквозь смех", "Смерть луны",
    "Сумасшедшим вход бесплатно", "Ты будешь гореть в аду",
    "Универсальный солдат", "Улетай",
    "Шаг назад (feat. UNVRS)", "Шизофрения (feat. Серафим)",
    "Шрам", "Чтобы не забыть (feat. МОЛОДОСТЬ ВНУТРИ)",
    "Эдем", "Эпитафия (feat. СИНЕРГИС)",
    "Я буду любить тебя вечно", "Ядовитые", "Я рассыпаю сахар"
]

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== КОМАНДЫ БОТА =====
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎵 ПЕРЕЙТИ К ОПРОСУ", url=SITE_URL),
        types.InlineKeyboardButton("🏆 ОБЩИЙ РЕЙТИНГ", callback_data="show_ranking"),
        types.InlineKeyboardButton("🔄 СБРОСИТЬ МОЙ ПРОГРЕСС", callback_data="reset_progress")
    )
    
    bot.send_message(
        message.chat.id,
        "🎵 **ASPER X · YOUR TOP**\n\n"
        "Создай свой идеальный рейтинг песен!\n\n"
        "📌 **Как это работает:**\n"
        "1. Перейди по ссылке\n"
        "2. Сравнивай песни попарно\n"
        "3. Получи свой топ\n\n"
        "🔗 **Ссылка на опрос:**",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_ranking")
def show_ranking(call):
    bot.answer_callback_query(call.id)
    # Пока заглушка — общий рейтинг будет позже
    bot.send_message(
        call.message.chat.id,
        "📊 **Общий рейтинг пока в разработке.**\n"
        "Скоро здесь появятся результаты всех участников!",
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "reset_progress")
def reset_progress(call):
    bot.answer_callback_query(call.id, "🔄 Прогресс сброшен!")
    bot.send_message(
        call.message.chat.id,
        "🔄 Твои данные сброшены. Теперь ты можешь пройти опрос заново по ссылке.",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.polling(none_stop=True)
