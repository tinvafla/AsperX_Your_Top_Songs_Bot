import telebot
from telebot import types
import json
import os
import math
from flask import Flask, request, jsonify
import threading

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
bot = telebot.TeleBot(TOKEN)

SITE_URL = "https://asperxyourtopsongs.netlify.app/"

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
GLOBAL_RANKING_FILE = "global_ranking.json"
USER_RESULTS_FILE = "user_results.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_global_ranking():
    if os.path.exists(GLOBAL_RANKING_FILE):
        with open(GLOBAL_RANKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_global_ranking(data):
    with open(GLOBAL_RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_user_results():
    if os.path.exists(USER_RESULTS_FILE):
        with open(USER_RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_results(data):
    with open(USER_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎵 ПЕРЕЙТИ К ОПРОСУ", url=SITE_URL),
        types.InlineKeyboardButton("🏆 ОБЩИЙ РЕЙТИНГ", callback_data="show_ranking")
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
    
    data = load_global_ranking()
    if not data:
        bot.send_message(call.message.chat.id, "📊 Пока нет голосов. Будь первым!")
        return
    
    sorted_songs = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    text = "🏆 **ОБЩИЙ РЕЙТИНГ (ТОП-3)**\n\n"
    for i, (song, score) in enumerate(sorted_songs[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {song} — {score} ⭐\n"
    
    if len(sorted_songs) > 10:
        text += f"\n... и ещё {len(sorted_songs) - 10} песен"
    
    text += f"\n\n📊 Всего участников: {len(load_user_results())}"
    
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

app = Flask(__name__)

@app.route('/save_results', methods=['POST'])
def save_results():
    try:
        data = request.get_json()
        results = data.get('results', {})
        
        if not results:
            return jsonify({"status": "error", "message": "No results"}), 400
        
        # Сортируем результаты по убыванию (топ-90)
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        # Сохраняем полный топ-90 пользователя
        user_results = load_user_results()
        user_id = f"user_{len(user_results) + 1}"
        user_results[user_id] = {
            "top_90": sorted_results,
            "top_3": sorted_results[:3]
        }
        save_user_results(user_results)
        
        # Отправляем топ-90 в личные сообщения админу
        admin_id = "ТВОЙ_TELEGRAM_ID"  # Замени на свой ID
        text = f"📊 **Новый результат!**\n\n"
        text += f"👤 Пользователь: {user_id}\n\n"
        text += "🏆 **ТОП-90**\n"
        for i, (song, score) in enumerate(sorted_results[:10], 1):
            text += f"{i}. {song} — {score} ⭐\n"
        if len(sorted_results) > 10:
            text += f"\n... и ещё {len(sorted_results) - 10} песен"
        
        try:
            bot.send_message(admin_id, text, parse_mode="Markdown")
        except:
            pass
        
        # Обновляем общий рейтинг (только топ-3)
        global_ranking = load_global_ranking()
        for song, score in sorted_results[:3]:
            if song in global_ranking:
                global_ranking[song] += score
            else:
                global_ranking[song] = score
        save_global_ranking(global_ranking)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Бот и сервер запущены...")
    bot.polling(none_stop=True)
