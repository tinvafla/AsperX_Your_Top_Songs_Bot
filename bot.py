import telebot
from telebot import types
import json
import os
from flask import Flask, request, jsonify
import threading
import datetime
from flask_cors import CORS
import random
import time

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
ADMIN_ID = "832018497"
bot = telebot.TeleBot(TOKEN)

SITE_URL = "https://tinvafla.github.io/AsperX_Your_Top_Songs_Site/"

GLOBAL_RANKING_FILE = "global_ranking.json"
USER_RESULTS_FILE = "user_results.json"
STATS_FILE = "stats.json"

user_states = {}

ALL_SONGS = [
    "Bad Trip", "Monsta", "Plague (feat. Ctrl+Freak)", "Sorry Not Sorry", "Stellar",
    "Über Ich", "Будет больно", "Был таким всегда (feat. aikko)", "В долгий путь",
    "Вместе", "Ветер перемен", "Всё разбито (feat. KASKAD, Совергон, VULPES VULT!, ПАНЦУШОТ, Танцы Сознания)",
    "Всё, что должно умереть", "Выстрели", "Волчок", "Делать", "Дело нескольких минут",
    "Демоны города Икс", "Держись", "Дрянь", "Дыхание", "Дышать и жить", "Заряжай",
    "Засыпай", "Земля", "Звёздная", "Змея", "Имя", "Ищи", "Если зовут",
    "Каждый справляется сам", "Каприз", "Карантинка", "Картонная", "Квадрат Декарта",
    "Классики (feat. tamagotchik)", "Колыбельная", "Космос", "Крики планет",
    "Курит и молчит (feat. Ar4ey)", "Лабиринт (feat. ЛИСН)", "Линии жизни",
    "Локус генома", "Любить", "Любовь и ненависть на улице Ленина", "Мой бог",
    "Море", "Мотыльки (feat. Port Avenue)", "Мы не железные", "Надо улыбаться",
    "Не выходи", "Не переживай", "Не люблю", "Незнакомка", "Никому не говори",
    "От автора", "Патрон", "Пей, лечись, люби (feat. Гарри Топор)", "Перелом",
    "Петь в тишине", "Питер Пэйн", "План", "Почти получилось", "Праздничная",
    "Право успеть", "Прикосноверие", "Приходи ко мне (feat. МОНТГОМЕРИ)",
    "Привидения", "Приметы (feat. ГОТЭМ)", "Прозерпина", "Просто поговорить",
    "Прости (feat. VULPES VULT!)", "ПТСР (feat. Ctrl+Freak)",
    "Пускай весь мир разлетается по кускам", "Пустота (feat. Ctrl+Freak)",
    "Радость", "Самая честная песня", "Сгораю", "Сказка (feat. Катя Лу)",
    "Скоро узнаешь", "Слёзы сквозь смех", "Смерть луны",
    "Сумасшедшим вход бесплатно", "Ты будешь гореть в аду", "Удачи, мистер Горски",
    "Универсальный солдат", "Улетай", "Шаг назад (feat. UNVRS)",
    "Шизофрения (feat. Серафим)", "Шрам", "Чтобы не забыть (feat. МОЛОДОСТЬ ВНУТРИ)",
    "Эдем", "Эпитафия (feat. DEEP-EX-SENSE, Лжедмитрий IV)",
    "Я буду любить тебя вечно", "Я рассыпаю сахар", "Ядовитые"
]

ACHIEVEMENTS = [
    {"count": 100, "message": "🎉 100 пользователей! Спасибо каждому!"},
    {"count": 500, "message": "🔥 500 пользователей! Мы растем!"},
    {"count": 1000, "message": "🌟 1000 пользователей! Это победа!"}
]

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_stats():
    if not os.path.exists(STATS_FILE):
        stats = {
            "users": {},
            "daily_activity": {},
            "total_actions": {
                "start": 0,
                "survey_visit": 0,
                "ranking_view": 0,
                "my_results": 0,
                "toggle_ranking": 0,
                "song_of_day": 0,
                "survey_complete": 0
            },
            "achievements": {},
            "song_of_day_stats": {}
        }
        save_json(STATS_FILE, stats)
    return load_json(STATS_FILE)

def update_stats(user_id, action):
    stats = load_json(STATS_FILE)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_id_str = str(user_id)
    
    if user_id_str not in stats["users"]:
        stats["users"][user_id_str] = {
            "first_visit": datetime.datetime.now().isoformat(),
            "last_visit": datetime.datetime.now().isoformat(),
            "actions": {}
        }
        
        try:
            user = bot.get_chat(int(user_id))
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
            username = f"@{user.username}" if user.username else "не установлен"
            bot.send_message(ADMIN_ID, f"👤 Новый пользователь!\n\nИмя: {name}\nНик: {username}\nID: {user_id}\n\nНачал диалог с ботом.")
        except:
            bot.send_message(ADMIN_ID, f"👤 Новый пользователь!\n\nID: {user_id}\n\nНачал диалог с ботом.")
        
        total_users = len(stats["users"])
        for achievement in ACHIEVEMENTS:
            if total_users == achievement["count"] and str(achievement["count"]) not in stats["achievements"]:
                stats["achievements"][str(achievement["count"])] = datetime.datetime.now().isoformat()
                bot.send_message(ADMIN_ID, f"🎉 ДОСТИЖЕНИЕ!\n\n👥 Количество пользователей достигло {achievement['count']}!\n\n{achievement['message']}")
    
    stats["users"][user_id_str]["last_visit"] = datetime.datetime.now().isoformat()
    if action not in stats["users"][user_id_str]["actions"]:
        stats["users"][user_id_str]["actions"][action] = 0
    stats["users"][user_id_str]["actions"][action] += 1
    
    if action in stats["total_actions"]:
        stats["total_actions"][action] += 1
    
    if today not in stats["daily_activity"]:
        stats["daily_activity"][today] = 0
    stats["daily_activity"][today] += 1
    
    save_json(STATS_FILE, stats)

def get_user_exclude_status(user_id):
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    
    if user_id_str not in user_results:
        return False
    
    user_data = user_results[user_id_str]
    
    if isinstance(user_data, dict):
        return user_data.get("exclude_from_ranking", False)
    
    return False

def set_user_exclude_status(user_id, status):
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    
    if user_id_str not in user_results:
        user_results[user_id_str] = {
            "top_90": [],
            "exclude_from_ranking": status,
            "is_complete": False
        }
    else:
        user_data = user_results[user_id_str]
        if isinstance(user_data, dict):
            user_data["exclude_from_ranking"] = status
        else:
            user_results[user_id_str] = {
                "top_90": user_data,
                "exclude_from_ranking": status,
                "is_complete": False
            }
    
    save_json(USER_RESULTS_FILE, user_results)

def get_user_info(user_id):
    try:
        user = bot.get_chat(int(user_id))
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"
        username = f"@{user.username}" if user.username else "не установлен"
        return name, username
    except:
        return f"User {user_id}", "неизвестен"

def get_menu_keyboard(user_id):
    is_excluded = get_user_exclude_status(user_id)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎵 ПЕРЕЙТИ К ОПРОСУ", url=f"{SITE_URL}?user_id={user_id}"),
        types.InlineKeyboardButton("📊 МОИ РЕЗУЛЬТАТЫ", callback_data="my_results"),
        types.InlineKeyboardButton("🏆 ОБЩИЙ РЕЙТИНГ", callback_data="show_ranking")
    )
    
    if is_excluded:
        keyboard.add(types.InlineKeyboardButton("🔓 УЧИТЫВАТЬ В ОБЩЕМ РЕЙТИНГЕ", callback_data="toggle_ranking"))
    else:
        keyboard.add(types.InlineKeyboardButton("🔒 НЕ УЧИТЫВАТЬ В ОБЩЕМ РЕЙТИНГЕ", callback_data="toggle_ranking"))
    
    keyboard.add(types.InlineKeyboardButton("🎵 ПЕСНЯ ДНЯ", callback_data="song_of_day"))
    keyboard.add(types.InlineKeyboardButton("📖 ИСТОРИЯ СОЗДАНИЯ", callback_data="story"))
    keyboard.add(types.InlineKeyboardButton("✉️ НАПИСАТЬ АВТОРУ", callback_data="write_author"))
    
    return keyboard

def send_new_menu(chat_id, user_id):
    keyboard = get_menu_keyboard(user_id)
    msg = bot.send_message(
        chat_id,
        "Выбери действие:",
        reply_markup=keyboard
    )
    
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["menu_message_id"] = msg.message_id
    return msg

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    init_stats()
    update_stats(user_id, "start")
    
    user_results = load_json(USER_RESULTS_FILE)
    user_id_str = str(user_id)
    
    if user_id_str not in user_results:
        user_results[user_id_str] = {
            "top_90": [],
            "exclude_from_ranking": False,
            "is_complete": False
        }
        save_json(USER_RESULTS_FILE, user_results)
    
    bot.send_message(
        message.chat.id,
        "🎵 <b>ASPER X · YOUR TOP SONGS</b>\n\n"
        "Перейди по ссылке, пройди опрос и получи свой топ!\n\n"
        "После завершения нажми <b>«Вернуться в бота»</b> или <b>«Мои результаты»</b>, чтобы получить свой топ.\n\n"
        "⏳ Тест займёт ~3–5 минут в зависимости от твоих решений.\n\n"
        "💡 Если захочешь перепройти опрос — просто нажми «Перейти к опросу» ещё раз. Старые результаты автоматически заменятся новыми.\n\n"
        "🛠️ Всё сделано на чистом энтузиазме, без опыта, но с любовью.\n\n"
        "<blockquote>У меня, может, и нет мозгов, господа, но у меня есть идея.</blockquote>\n\n"
        "💬 Любая обратная связь приветствуется!",
        parse_mode="HTML"
    )
    
    send_new_menu(message.chat.id, user_id)

@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    help_text = """
📖 **ПОМОЩЬ АДМИНИСТРАТОРА**

**Доступные команды:**

/start - Главное меню
/stats - Статистика бота
/help - Эта справка
/export - Экспорт всех данных (бэкап)
/import - Импорт данных из бэкапа (пришли файл)
/announce - Сделать рассылку всем пользователям

**📊 Статистика показывает:**
• Всего пользователей
• Кто загрузил результаты
• Активность за сегодня/неделю/всё время
• Достижения (100, 500, 1000 пользователей)

**📨 Рассылка:**
/announce - напиши текст, и он отправится всем пользователям

**💾 Бэкап:**
/export - создаёт JSON файл со всеми данными
/import - восстановить данные из бэкапа

**🎵 Песня дня:**
Доступна в меню бота. Показывает случайную песню из списка.

**🔒 Учитывать/не учитывать:**
Пользователи могут сами решать, участвовать ли в общем рейтинге.

**📱 Сайт опроса:**
{SITE_URL}

**✉️ Обратная связь:**
Пользователи могут писать автору через кнопку в меню.

---

*Бот создан с ❤️ для Asper X и фандома*
    """.format(SITE_URL=SITE_URL)
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    stats = load_json(STATS_FILE)
    user_results = load_json(USER_RESULTS_FILE)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    total_users = len(stats["users"])
    completed = len([u for u in user_results.values() if isinstance(u, dict) and u.get("is_complete", False)])
    survey_completes = stats["total_actions"].get("survey_complete", 0)
    
    today_activity = stats["daily_activity"].get(today, 0)
    week_activity = sum(count for date, count in stats["daily_activity"].items() if date >= week_ago)
    all_time_activity = sum(stats["daily_activity"].values())
    
    text = "📊 **СТАТИСТИКА БОТА**\n\n"
    text += f"👥 **Всего пользователей:** {total_users}\n"
    text += f"✅ **Загрузили результат:** {completed} (всего {survey_completes} прохождений)\n\n"
    
    text += "📈 **Активность:**\n"
    text += f"📅 Сегодня: {today_activity} 👤\n"
    text += f"📅 За неделю: {week_activity} 👤\n"
    text += f"📅 За всё время: {all_time_activity} 👤\n\n"
    
    text += "🏆 **Достижения:**\n"
    for achievement in ACHIEVEMENTS:
        if str(achievement["count"]) in stats["achievements"]:
            text += f"✅ {achievement['count']} пользователей - ДОСТИГНУТО!\n"
        else:
            if achievement["count"] > total_users:
                text += f"⏳ {achievement['count']} пользователей - осталось {achievement['count'] - total_users}\n"
    
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['announce'])
def announce_command(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    bot.reply_to(message, "✏️ Напиши текст рассылки для всех пользователей:")
    user_states[message.from_user.id] = "waiting_for_announce"

@bot.message_handler(commands=['export'])
def export_data(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    try:
        user_results = load_json(USER_RESULTS_FILE)
        global_ranking = load_json(GLOBAL_RANKING_FILE)
        stats = load_json(STATS_FILE)
        
        data = {
            "users": user_results,
            "global_ranking": global_ranking,
            "stats": stats,
            "export_date": str(datetime.datetime.now())
        }
        
        bot.send_document(
            message.chat.id,
            json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'),
            visible_file_name='bot_data_backup.json'
        )
        bot.reply_to(message, "✅ Бэкап отправлен!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['import'])
def import_command(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    bot.reply_to(message, "📤 Отправь JSON файл с бэкапом (файл, который получил через /export)")
    user_states[message.from_user.id] = "waiting_for_import"

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    
    if user_id in user_states and user_states[user_id] == "waiting_for_import":
        if message.from_user.id != int(ADMIN_ID):
            return
        
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            data = json.loads(downloaded_file.decode('utf-8'))
            
            if "users" in data:
                save_json(USER_RESULTS_FILE, data["users"])
            if "global_ranking" in data:
                save_json(GLOBAL_RANKING_FILE, data["global_ranking"])
            if "stats" in data:
                save_json(STATS_FILE, data["stats"])
            
            bot.reply_to(message, "✅ Данные успешно восстановлены из бэкапа!")
            
            del user_states[user_id]
            
        except json.JSONDecodeError:
            bot.reply_to(message, "❌ Ошибка: файл не является корректным JSON")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при импорте: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "toggle_ranking")
def toggle_ranking(call):
    user_id = call.from_user.id
    is_excluded = get_user_exclude_status(user_id)
    
    if is_excluded:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("✅ ДА, УЧИТЫВАТЬ", callback_data="confirm_include"),
            types.InlineKeyboardButton("❌ ОТМЕНА", callback_data="cancel_toggle")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "🔓 Ты уверен, что хочешь снова учитывать свои результаты в общем рейтинге?\n\nТвои голоса снова будут влиять на общий топ.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("✅ ДА, НЕ УЧИТЫВАТЬ", callback_data="confirm_exclude"),
            types.InlineKeyboardButton("❌ ОТМЕНА", callback_data="cancel_toggle")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "🔒 Ты уверен, что хочешь исключить свои результаты из общего рейтинга?\n\nТвои голоса больше не будут влиять на общий топ.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

@bot.callback_query_handler(func=lambda call: call.data == "confirm_include")
def confirm_include(call):
    user_id = call.from_user.id
    update_stats(user_id, "toggle_ranking")
    
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    global_ranking = load_json(GLOBAL_RANKING_FILE)
    points = [5, 3, 1]
    
    top_90 = []
    if user_id_str in user_results:
        user_data = user_results[user_id_str]
        if isinstance(user_data, dict):
            top_90 = user_data.get("top_90", [])
        else:
            top_90 = user_data
    
    if top_90 and len(top_90) >= 3:
        for idx, (song, _) in enumerate(top_90[:3]):
            if song in global_ranking:
                global_ranking[song] += points[idx]
            else:
                global_ranking[song] = points[idx]
        save_json(GLOBAL_RANKING_FILE, global_ranking)
    
    set_user_exclude_status(user_id, False)
    
    name, username = get_user_info(user_id)
    admin_msg = f"🔓 Пользователь изменил статус\n\n"
    admin_msg += f"👤 Имя: {name}\n"
    admin_msg += f"🔗 Ник: {username}\n"
    admin_msg += f"🆔 ID: {user_id}\n\n"
    admin_msg += "✅ Теперь УЧИТЫВАЕТСЯ в общем рейтинге"
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    bot.answer_callback_query(call.id, "✅ Готово!")
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_exclude")
def confirm_exclude(call):
    user_id = call.from_user.id
    update_stats(user_id, "toggle_ranking")
    
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    global_ranking = load_json(GLOBAL_RANKING_FILE)
    points = [5, 3, 1]
    
    top_90 = []
    if user_id_str in user_results:
        user_data = user_results[user_id_str]
        if isinstance(user_data, dict):
            top_90 = user_data.get("top_90", [])
        else:
            top_90 = user_data
    
    if top_90 and len(top_90) >= 3:
        for idx, (song, _) in enumerate(top_90[:3]):
            if song in global_ranking:
                global_ranking[song] -= points[idx]
                if global_ranking[song] <= 0:
                    del global_ranking[song]
        save_json(GLOBAL_RANKING_FILE, global_ranking)
    
    set_user_exclude_status(user_id, True)
    
    name, username = get_user_info(user_id)
    admin_msg = f"🔒 Пользователь изменил статус\n\n"
    admin_msg += f"👤 Имя: {name}\n"
    admin_msg += f"🔗 Ник: {username}\n"
    admin_msg += f"🆔 ID: {user_id}\n\n"
    admin_msg += "❌ Теперь НЕ УЧИТЫВАЕТСЯ в общем рейтинге"
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    bot.answer_callback_query(call.id, "✅ Готово!")
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_toggle")
def cancel_toggle(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "❌ Отменено")
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "song_of_day")
def song_of_day(call):
    user_id = call.from_user.id
    update_stats(user_id, "song_of_day")
    bot.answer_callback_query(call.id)
    
    song = random.choice(ALL_SONGS)
    
    stats = load_json(STATS_FILE)
    if song not in stats["song_of_day_stats"]:
        stats["song_of_day_stats"][song] = 0
    stats["song_of_day_stats"][song] += 1
    save_json(STATS_FILE, stats)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎲 ДРУГАЯ ПЕСНЯ", callback_data="song_of_day"),
        types.InlineKeyboardButton("🔙 ВЕРНУТЬСЯ В МЕНЮ", callback_data="back_to_menu")
    )
    
    bot.edit_message_text(
        f"🎵 **ПЕСНЯ ДНЯ**\n\n"
        f"🎶 {song}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "story")
def story(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✉️ НАПИСАТЬ АВТОРУ", callback_data="write_author"),
        types.InlineKeyboardButton("🔙 ВЕРНУТЬСЯ НАЗАД", callback_data="back_to_menu")
    )
    
    bot.edit_message_text(
        "📖 **ИСТОРИЯ СОЗДАНИЯ**\n\n"
        "Привет! 👋\n\n"
        "Я tinvafla, или вафелька — как тебе удобнее. И я та самая, кто собрала этого бота на голом энтузиазме.\n\n"
        "Дело было вечером, делать было нечего... или как это обычно бывает. Мне захотелось составить свой тир-лист песен Asper X. Я искала платформу, где можно было бы сравнивать треки, составлять личный топ, видеть, что выбирают другие — и не нашла. Ничего. Совсем.\n\n"
        "Тогда я подумала: «А почему бы не сделать это самой?»\n\n"
        "У меня не было опыта. Вообще. Ни строчки кода до этого. Но были нейросети, пара свободных вечеров и огромное желание. Так появился этот бот и сайт. С нуля, с идеей, с багами и с любовью.\n\n"
        "Собрала 90 песен Asper X — ровно столько, сколько нашла. Если что-то пропустила — пишите, исправлюсь! Здесь только основной проект, без RetroElektro и других ответвлений, хотя они тоже крутые и, надеюсь, до них руки дойдут тоже.\n\n"
        "В мечтах — добавить короткие превью к песням (секунд по 5), чтобы можно было вспомнить трек, если название не говорит само за себя. Но тут сложность с авторскими правами, поэтому пока не готова. Если этот бот найдёт отклик у аудитории — я вернусь к этой идее и, при одобрении исполнителя музыки, может быть, добавлю.\n\n"
        "Версия 1.0 — тестовая. Своих серверов для хранения данных у меня нет, и жизнеспособность этого бота покажет, стоит ли заморачиваться над точностью общего рейтинга песен среди всех прошедших опрос, так как каждое обновление обнуляет все предыдущие результаты опросов. А может, я зря волнуюсь.\n\n"
        "Всё это сделано одним человечком (мной) из искренней любви к творчеству группы Asper X и Тима Эрны. Гиперфиксации нейроотличных умных людей творят чудеса. Очень жду 27 октября, чтобы выразить свою любовь вживую 🫶\n\n"
        "Спасибо, что вы здесь. Что проходите опрос. Что помогаете делать этот рейтинг живым.\n\n"
        "Связаться со мной можно через функционал бота — я читаю всё 💬",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "my_results")
def my_results(call):
    user_id = call.from_user.id
    update_stats(user_id, "my_results")
    bot.answer_callback_query(call.id, "📊 Загружаю твои результаты...")
    
    user_results = load_json(USER_RESULTS_FILE)
    user_id_str = str(user_id)
    
    if user_id_str in user_results:
        user_data = user_results[user_id_str]
        if isinstance(user_data, dict):
            top_90 = user_data.get("top_90", [])
        else:
            top_90 = user_data
        
        if top_90:
            text = "🏆 **ТВОЙ ТОП**\n\n"
            for i, (song, score) in enumerate(top_90, 1):
                text += f"{i}. {song}\n"
            
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            send_new_menu(call.message.chat.id, user_id)
        else:
            bot.edit_message_text(
                "❌ **У тебя нет сохранённых результатов!**\n\nПерейди по ссылке и пройди опрос, чтобы получить свой топ.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            send_new_menu(call.message.chat.id, user_id)
    else:
        bot.edit_message_text(
            "❌ **Ты ещё не проходил опрос!**\n\nПерейди по ссылке и пройди опрос, чтобы получить свой топ.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "write_author")
def write_author(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_for_author_message"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ ОТМЕНА", callback_data="cancel_author"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "📝 Напиши своё пожелание, вопрос или отзыв.\n\nЯ передам это автору.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "cancel_author")
def cancel_author(call):
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    bot.answer_callback_query(call.id, "❌ Отменено")
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "show_ranking")
def show_ranking_callback(call):
    user_id = call.from_user.id
    update_stats(user_id, "ranking_view")
    bot.answer_callback_query(call.id)
    
    data = load_json(GLOBAL_RANKING_FILE)
    if not data:
        bot.edit_message_text(
            "📊 Пока нет голосов. Будь первым!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        send_new_menu(call.message.chat.id, user_id)
        return

    user_results = load_json(USER_RESULTS_FILE)
    voters_count = 0
    for u in user_results.values():
        if isinstance(u, dict):
            if not u.get("exclude_from_ranking", False):
                voters_count += 1
        else:
            voters_count += 1

    sorted_songs = sorted(data.items(), key=lambda x: x[1], reverse=True)
    text = f"🏆 **ОБЩИЙ РЕЙТИНГ**\n👥 Участников: {voters_count}\n\n"
    
    current_place = 1
    for i, (song, score) in enumerate(sorted_songs, 1):
        if i > 1 and sorted_songs[i-1][1] != sorted_songs[i-2][1]:
            current_place = i
        medal = "🥇" if current_place == 1 else "🥈" if current_place == 2 else "🥉" if current_place == 3 else f"{current_place}."
        text += f"{medal} {song}\n"
        if i >= 20:
            break
    
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def reply_to_user(call):
    user_id = call.data.replace("reply_", "")
    admin_id = call.from_user.id
    
    if admin_id != int(ADMIN_ID):
        bot.answer_callback_query(call.id, "❌ У вас нет прав!")
        return
    
    user_states[admin_id] = f"reply_{user_id}"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ ОТМЕНА", callback_data="cancel_reply"))
    
    try:
        user = bot.get_chat(int(user_id))
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"
        username = f"@{user.username}" if user.username else f"ID: {user_id}"
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"✏️ Ответ для {username}:\n\nНапиши своё сообщение, и я передам его пользователю.",
            reply_markup=keyboard
        )
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_reply")
def cancel_reply(call):
    admin_id = call.from_user.id
    if admin_id in user_states:
        del user_states[admin_id]
    bot.answer_callback_query(call.id, "❌ Отменено")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "❌ Отправка отменена.")
    send_new_menu(call.message.chat.id, admin_id)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == "waiting_for_announce":
            if message.from_user.id != int(ADMIN_ID):
                return
            
            if not message.text or message.text.strip() == "":
                bot.reply_to(message, "❌ Текст не может быть пустым.")
                return
            
            stats = load_json(STATS_FILE)
            sent = 0
            failed = 0
            
            bot.reply_to(message, "📨 Начинаю рассылку...")
            
            for user_id_str in stats["users"].keys():
                try:
                    bot.send_message(int(user_id_str), f"📢 **Объявление от автора:**\n\n{message.text}", parse_mode="Markdown")
                    sent += 1
                    time.sleep(0.05)
                except:
                    failed += 1
            
            bot.send_message(ADMIN_ID, f"✅ Рассылка завершена!\n\n📨 Отправлено: {sent}\n❌ Не доставлено: {failed}")
            del user_states[user_id]
        
        elif state == "waiting_for_author_message":
            if not message.text or message.text.strip() == "":
                bot.reply_to(message, "❌ Сообщение не может быть пустым. Напиши что-нибудь.")
                return
            
            try:
                user = bot.get_chat(user_id)
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
                username = f"@{user.username}" if user.username else "не установлен"
                
                msg = f"✉️ **Новое сообщение от пользователя**\n\n"
                msg += f"👤 Имя: {name}\n"
                msg += f"🔗 Ник: {username}\n"
                msg += f"🆔 ID: {user_id}\n\n"
                msg += f"📝 Текст:\n{message.text}"
                
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(types.InlineKeyboardButton("📩 ОТВЕТИТЬ", callback_data=f"reply_{user_id}"))
                
                bot.send_message(ADMIN_ID, msg, parse_mode="Markdown", reply_markup=keyboard)
                bot.reply_to(message, "✅ Спасибо! Твоё сообщение передано автору.")
                del user_states[user_id]
                
                send_new_menu(message.chat.id, user_id)
            except Exception as e:
                bot.reply_to(message, "❌ Ошибка при отправке. Попробуй позже.")
                print(f"Ошибка: {e}")
        
        elif state.startswith("reply_"):
            target_user_id = state.replace("reply_", "")
            if not message.text or message.text.strip() == "":
                bot.reply_to(message, "❌ Сообщение не может быть пустым.")
                return
            
            try:
                bot.send_message(
                    int(target_user_id),
                    f"✉️ **Сообщение от автора:**\n\n{message.text}"
                )
                bot.reply_to(message, "✅ Сообщение отправлено пользователю.")
                del user_states[user_id]
                
                send_new_menu(message.chat.id, user_id)
            except Exception as e:
                bot.reply_to(message, "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")
                print(f"Ошибка: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/save_results', methods=['POST'])
def save_results():
    try:
        data = request.get_json()
        print("📥 ПОЛУЧЕНЫ ДАННЫЕ:", data)
        
        user_id = data.get('user_id', 'anonymous')
        top_90 = data.get('top_90', [])
        is_complete = data.get('is_complete', False)
        
        print("👤 user_id:", user_id)
        print("📊 Количество песен в top_90:", len(top_90))
        print("✅ Тест пройден полностью:", is_complete)

        if not top_90:
            print("❌ top_90 пустой!")
            return jsonify({"status": "error", "message": "No top_90"}), 400

        if not is_complete:
            print("⚠️ Тест не пройден полностью — результаты НЕ сохранены в общий рейтинг")
            try:
                user = bot.get_chat(int(user_id))
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
                username = f"@{user.username}" if user.username else "не установлен"
                
                text = f"⚠️ **Досрочное завершение от {name}**\n\n"
                text += f"👤 Имя: {name}\n"
                text += f"🔗 Ник: {username}\n"
                text += f"🆔 ID: {user_id}\n\n"
                text += "Тест не был пройден полностью, результаты НЕ добавлены в общий рейтинг."
                
                bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
            except:
                pass
            
            try:
                user_results = load_json(USER_RESULTS_FILE)
                exclude_status = False
                if user_id in user_results and isinstance(user_results[user_id], dict):
                    exclude_status = user_results[user_id].get("exclude_from_ranking", False)
                
                user_results[user_id] = {
                    "top_90": top_90,
                    "exclude_from_ranking": exclude_status,
                    "is_complete": False
                }
                save_json(USER_RESULTS_FILE, user_results)
                print("✅ Неполные результаты сохранены в историю пользователя")
            except:
                pass
            
            return jsonify({"status": "success", "note": "incomplete_results_saved_locally"}), 200

        user_results = load_json(USER_RESULTS_FILE)
        global_ranking = load_json(GLOBAL_RANKING_FILE)
        points = [5, 3, 1]
        
        exclude_status = False
        if user_id in user_results and isinstance(user_results[user_id], dict):
            exclude_status = user_results[user_id].get("exclude_from_ranking", False)
        
        if user_id in user_results:
            user_data = user_results[user_id]
            if isinstance(user_data, dict):
                old_top_90 = user_data.get("top_90", [])
            else:
                old_top_90 = user_data
            
            if old_top_90 and len(old_top_90) >= 3:
                old_top_3 = old_top_90[:3]
                for idx, (song, _) in enumerate(old_top_3):
                    if song in global_ranking:
                        global_ranking[song] -= points[idx]
                        if global_ranking[song] <= 0:
                            del global_ranking[song]
        
        user_results[user_id] = {
            "top_90": top_90,
            "exclude_from_ranking": exclude_status,
            "is_complete": True
        }
        save_json(USER_RESULTS_FILE, user_results)
        
        update_stats(int(user_id), "survey_complete")
        
        print(f"✅ Результаты сохранены для: {user_id}, статус: {'ИСКЛЮЧЕН' if exclude_status else 'УЧИТЫВАЕТСЯ'}")

        if user_id != 'anonymous':
            try:
                text = "🏆 **ТВОЙ ТОП**\n\n"
                for i, (song, score) in enumerate(top_90, 1):
                    text += f"{i}. {song}\n"
                bot.send_message(int(user_id), text, parse_mode="Markdown")
                print("✅ Топ отправлен пользователю:", user_id)
            except Exception as e:
                print(f"❌ Ошибка отправки пользователю: {e}")

        try:
            user = bot.get_chat(int(user_id))
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
            username = f"@{user.username}" if user.username else "не установлен"
            
            text = f"📊 **Новый топ-3 от {name}**\n\n"
            text += f"👤 Имя: {name}\n"
            text += f"🔗 Ник: {username}\n"
            text += f"🆔 ID: {user_id}\n"
            text += f"📌 Статус: {'ИСКЛЮЧЕН из рейтинга' if exclude_status else 'УЧИТЫВАЕТСЯ в рейтинге'}\n\n"
            for i, (song, score) in enumerate(top_90[:3], 1):
                text += f"{i}. {song}\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton("📩 ОТВЕТИТЬ", callback_data=f"reply_{user_id}"))
            
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown", reply_markup=keyboard)
            print("✅ Топ-3 отправлен админу")
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")

        if not exclude_status:
            for idx, (song, _) in enumerate(top_90[:3]):
                if song in global_ranking:
                    global_ranking[song] += points[idx]
                else:
                    global_ranking[song] = points[idx]
            save_json(GLOBAL_RANKING_FILE, global_ranking)
            print("✅ Общий рейтинг обновлён")
        else:
            print("ℹ️ Пользователь исключён из общего рейтинга")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ ОШИБКА:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Бот и сервер запущены...")
    bot.polling(none_stop=True)
