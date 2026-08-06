import telebot
from telebot import types
import json
import os
import math

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
bot = telebot.TeleBot(TOKEN)

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

def expected(a, b):
    return 1 / (1 + math.pow(10, (b - a) / 400))

def update_elo(winner_elo, loser_elo):
    k = 32
    ew = expected(winner_elo, loser_elo)
    el = expected(loser_elo, winner_elo)
    new_winner = round(winner_elo + k * (1 - ew))
    new_loser = round(loser_elo + k * (0 - el))
    return new_winner, new_loser

def get_user_data(user_id):
    data = load_data()
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "songs": {song: {"elo": 1000, "wins": 0, "losses": 0, "played": 0} for song in SONGS},
            "compared": [],
            "skipped": [],
            "favorites": []
        }
        save_data(data)
    return data["users"][str(user_id)]

def save_user_data(user_id, user_data):
    data = load_data()
    data["users"][str(user_id)] = user_data
    save_data(data)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎵 **ASPER X · YOUR TOP**\n\n"
        "Сравнивай песни и создавай свой идеальный рейтинг!\n\n"
        "📌 **Команды:**\n"
        "/vote — сравнить две песни\n"
        "/ranking — показать топ\n"
        "/skip — пропустить песню\n"
        "/favorite — добавить в избранное\n"
        "/reset — начать заново\n"
        "/help — помощь",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "🎯 **Как это работает:**\n\n"
        "1. Бот предлагает две песни\n"
        "2. Ты выбираешь лучшую кнопкой\n"
        "3. Рейтинг обновляется по системе Elo\n"
        "4. В конце ты получаешь свой топ\n\n"
        "❤️ — добавь в избранное\n"
        "⏭️ — пропусти песню (не влияет на рейтинг)",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['vote'])
def vote(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    active = [s for s in SONGS if s not in user_data["skipped"]]
    
    if len(active) < 2:
        bot.send_message(message.chat.id, "🎉 Все песни оценены! Нажми /ranking")
        return
    
    found = False
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            if [active[i], active[j]] not in user_data["compared"] and [active[j], active[i]] not in user_data["compared"]:
                song1, song2 = active[i], active[j]
                found = True
                break
        if found:
            break
    
    if not found:
        song1, song2 = active[0], active[1]
    
    user_data["current_pair"] = [song1, song2]
    save_user_data(user_id, user_data)
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(f"🎵 {song1}", callback_data=f"vote_{song1}")
    btn2 = types.InlineKeyboardButton(f"🎵 {song2}", callback_data=f"vote_{song2}")
    keyboard.add(btn1, btn2)
    
    fav1 = types.InlineKeyboardButton("❤️", callback_data=f"fav_{song1}")
    fav2 = types.InlineKeyboardButton("❤️", callback_data=f"fav_{song2}")
    skip1 = types.InlineKeyboardButton("⏭️", callback_data=f"skip_{song1}")
    skip2 = types.InlineKeyboardButton("⏭️", callback_data=f"skip_{song2}")
    keyboard.row(fav1, skip1)
    keyboard.row(fav2, skip2)
    keyboard.row(types.InlineKeyboardButton("🏆 Рейтинг", callback_data="show_ranking"))
    
    bot.send_message(
        message.chat.id,
        f"**{song1}**\n\n— ИЛИ —\n\n**{song2}**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('vote_'))
def handle_vote(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    
    winner = call.data.replace('vote_', '')
    pair = user_data.get("current_pair", [])
    
    if not pair:
        bot.answer_callback_query(call.id, "Ошибка. Попробуй /vote")
        return
    
    loser = pair[0] if pair[0] != winner else pair[1]
    
    w_elo = user_data["songs"][winner]["elo"]
    l_elo = user_data["songs"][loser]["elo"]
    new_w, new_l = update_elo(w_elo, l_elo)
    
    user_data["songs"][winner]["elo"] = new_w
    user_data["songs"][loser]["elo"] = new_l
    user_data["songs"][winner]["wins"] += 1
    user_data["songs"][loser]["losses"] += 1
    user_data["songs"][winner]["played"] += 1
    user_data["songs"][loser]["played"] += 1
    
    user_data["compared"].append(pair)
    user_data["current_pair"] = []
    
    save_user_data(user_id, user_data)
    
    bot.answer_callback_query(call.id, f"✅ Ты выбрал {winner}!")
    bot.edit_message_text(
        f"✅ **{winner}** победил!\n\n"
        f"📊 Новый рейтинг:\n"
        f"{winner}: {new_w} (+{new_w - w_elo})\n"
        f"{loser}: {new_l} ({new_l - l_elo})",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🎯 Следующее сравнение", callback_data="next_vote"))
    keyboard.add(types.InlineKeyboardButton("🏆 Рейтинг", callback_data="show_ranking"))
    bot.send_message(call.message.chat.id, "Продолжим?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "next_vote")
def next_vote(call):
    bot.answer_callback_query(call.id)
    vote(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def handle_fav(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    song = call.data.replace('fav_', '')
    
    if song not in user_data["favorites"]:
        user_data["favorites"].append(song)
        save_user_data(user_id, user_data)
        bot.answer_callback_query(call.id, f"❤️ {song} в избранном!")
        bot.send_message(call.message.chat.id, f"❤️ Добавлено в избранное: **{song}**", parse_mode="Markdown")
    else:
        user_data["favorites"].remove(song)
        save_user_data(user_id, user_data)
        bot.answer_callback_query(call.id, f"💔 {song} удалена из избранного")
        bot.send_message(call.message.chat.id, f"💔 **{song}** удалена из избранного", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('skip_'))
def handle_skip(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    song = call.data.replace('skip_', '')
    
    if song not in user_data["skipped"]:
        user_data["skipped"].append(song)
        save_user_data(user_id, user_data)
        bot.answer_callback_query(call.id, f"⏭️ {song} пропущена!")
        bot.send_message(call.message.chat.id, f"⏭️ **{song}** больше не участвует в рейтинге", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_ranking")
def show_ranking_callback(call):
    bot.answer_callback_query(call.id)
    ranking(call.message)

@bot.message_handler(commands=['ranking'])
def ranking(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    active = [(s, user_data["songs"][s]) for s in SONGS if s not in user_data["skipped"]]
    sorted_songs = sorted(active, key=lambda x: x[1]["elo"], reverse=True)
    
    if not sorted_songs:
        bot.send_message(message.chat.id, "Нет активных песен. Начни с /vote")
        return
    
    text = "🏆 **ТВОЙ ТОП**\n\n"
    for i, (song, data) in enumerate(sorted_songs[:15], 1):
        fav = " ❤️" if song in user_data["favorites"] else ""
        text += f"{i}. {song}{fav} — {data['elo']} ⭐\n"
    
    if len(sorted_songs) > 15:
        text += f"\n... и ещё {len(sorted_songs) - 15} песен"
    
    text += f"\n\n📊 Всего оценено: {len(sorted_songs)} песен"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = message.from_user.id
    data = load_data()
    if str(user_id) in data["users"]:
        del data["users"][str(user_id)]
        save_data(data)
    bot.send_message(message.chat.id, "🔄 Данные сброшены! Начни заново с /vote")

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.polling(none_stop=True)