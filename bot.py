import telebot
from telebot import types
import json
import os
from flask import Flask, request, jsonify
import threading
import datetime
from flask_cors import CORS
import random
import schedule
import time
import zipfile

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
ADMIN_ID = "832018497"
bot = telebot.TeleBot(TOKEN)

SITE_URL = "https://tinvafla.github.io/AsperX_Your_Top_Songs_Site/"

GLOBAL_RANKING_FILE = "global_ranking.json"
USER_RESULTS_FILE = "user_results.json"
STATS_FILE = "stats.json"
BACKUP_FOLDER = "backups"

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
    {"count": 10, "message": "🎉 Первые 10 пользователей!"},
    {"count": 50, "message": "🔥 Уже 50 человек с нами!"},
    {"count": 100, "message": "🌟 Сотня! Спасибо каждому!"},
    {"count": 200, "message": "🚀 200 пользователей! Мы растем!"},
    {"count": 500, "message": "💪 Полтысячи! Офигеть!"},
    {"count": 1000, "message": "👑 Тысяча! Это победа!"},
    {"count": 2500, "message": "🌟 2500! Вы лучшие!"},
    {"count": 5000, "message": "🎊 5000! Невероятно!"},
    {"count": 10000, "message": "💎 10000! Легендарно!"}
]

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        
        total_users = len(stats["users"])
        for achievement in ACHIEVEMENTS:
            if total_users == achievement["count"] and str(achievement["count"]) not in stats["achievements"]:
                stats["achievements"][str(achievement["count"])] = datetime.datetime.now().isoformat()
                bot.send_message(ADMIN_ID, f"🎉 ДОСТИЖЕНИЕ!\n\n👥 Количество пользователей достигло {achievement['count']}!\n\n{achievement['message']}\n\nСледующая цель: {get_next_achievement(total_users)}")
    
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

def get_next_achievement(total_users):
    for achievement in ACHIEVEMENTS:
        if achievement["count"] > total_users:
            return f"{achievement['count']} пользователей (осталось {achievement['count'] - total_users})"
    return "Новых целей пока нет 🎯"

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

def create_backup():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = f"{BACKUP_FOLDER}/backup_{timestamp}.json"
    
    data = {
        "global_ranking": load_json(GLOBAL_RANKING_FILE),
        "user_results": load_json(USER_RESULTS_FILE),
        "stats": load_json(STATS_FILE),
        "backup_time": datetime.datetime.now().isoformat()
    }
    
    save_json(backup_file, data)
    
    bot.send_message(ADMIN_ID, f"✅ Бэкап создан: backup_{timestamp}.json")
    
    manage_old_backups()
    send_daily_report()

def manage_old_backups():
    if not os.path.exists(BACKUP_FOLDER):
        return
    
    backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith("backup_") and f.endswith(".json")])
    
    if len(backups) > 30:
        old_backups = backups[:-30]
        archive_name = f"{BACKUP_FOLDER}/old_backups_{datetime.datetime.now().strftime('%Y-%m-%d')}.zip"
        
        with zipfile.ZipFile(archive_name, 'w') as zipf:
            for file in old_backups:
                file_path = os.path.join(BACKUP_FOLDER, file)
                zipf.write(file_path, file)
                os.remove(file_path)
        
        bot.send_document(
            ADMIN_ID,
            open(archive_name, 'rb'),
            visible_file_name=f'old_backups_{datetime.datetime.now().strftime("%Y-%m-%d")}.zip'
        )
        
        os.remove(archive_name)
        bot.send_message(ADMIN_ID, f"🗑️ Старые бэкапы заархивированы и удалены. Сохранено {len(backups[-30:])} последних бэкапов.")

def send_daily_report():
    stats = load_json(STATS_FILE)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    total_users = len(stats["users"])
    
    today_activity = stats["daily_activity"].get(today, 0)
    yesterday_activity = stats["daily_activity"].get(yesterday, 0)
    
    new_users_today = 0
    for user_id, user_data in stats["users"].items():
        if user_data.get("first_visit", "").startswith(today):
            new_users_today += 1
    
    report = f"📊 ЕЖЕДНЕВНЫЙ ОТЧЁТ ЗА {today}\n\n"
    report += f"👥 Новые пользователи: +{new_users_today}\n\n"
    report += f"📈 Активность за день:\n"
    report += f"- Запусков бота: {stats['total_actions'].get('start', 0)}\n"
    report += f"- Переходов к опросу: {stats['total_actions'].get('survey_visit', 0)}\n"
    report += f"- Просмотров рейтинга: {stats['total_actions'].get('ranking_view', 0)}\n"
    report += f"- Смен статуса: {stats['total_actions'].get('toggle_ranking', 0)}\n\n"
    report += f"📊 Статистика сегодня/вчера:\n"
    report += f"- Сегодня: {today_activity} 👤\n"
    report += f"- Вчера: {yesterday_activity} 👤\n\n"
    report += f"👥 Всего пользователей: {total_users}\n"
    report += f"🎯 Следующее достижение: {get_next_achievement(total_users)}\n"
    report += f"🏆 Песен в рейтинге: {len(load_json(GLOBAL_RANKING_FILE))}\n\n"
    report += f"✅ Бэкап создан: backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    
    bot.send_message(ADMIN_ID, report, parse_mode="Markdown")

def run_scheduler():
    schedule.every().day.at("02:00").do(create_backup)
    while True:
        schedule.run_pending()
        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
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
                "song_of_day": 0
            },
            "achievements": {},
            "song_of_day_stats": {},
            "last_daily_report": None
        }
        save_json(STATS_FILE, stats)
    
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

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != int(ADMIN_ID):
        bot.reply_to(message, "⛔ У вас нет прав на эту команду.")
        return
    
    stats = load_json(STATS_FILE)
    user_results = load_json(USER_RESULTS_FILE)
    global_ranking = load_json(GLOBAL_RANKING_FILE)
    
    total_users = len(stats["users"])
    completed = len([u for u in stats["users"].values() if u.get("actions", {}).get("survey_visit", 0) > 0])
    excluded = len([u for u in user_results.values() if isinstance(u, dict) and u.get("exclude_from_ranking", False)])
    
    text = "📊 **СТАТИСТИКА БОТА**\n\n"
    text += f"👥 Всего пользователей: {total_users}\n"
    text += f"✅ Прошли опрос полностью: {completed}\n"
    text += f"❌ Не завершили опрос: {total_users - completed}\n"
    text += f"🔒 Исключены из рейтинга: {excluded}\n"
    text += f"🏆 Песен в рейтинге: {len(global_ranking)}\n\n"
    
    text += "📈 **Активность ЗА ВСЁ ВРЕМЯ:**\n"
    text += f"- Запусков бота: {stats['total_actions'].get('start', 0)}\n"
    text += f"- Переходов к опросу: {stats['total_actions'].get('survey_visit', 0)}\n"
    text += f"- Просмотров рейтинга: {stats['total_actions'].get('ranking_view', 0)}\n"
    text += f"- Просмотров своих результатов: {stats['total_actions'].get('my_results', 0)}\n"
    text += f"- Смен статуса: {stats['total_actions'].get('toggle_ranking', 0)}\n"
    text += f"- Просмотров песни дня: {stats['total_actions'].get('song_of_day', 0)}\n\n"
    
    text += "📅 **Активность по дням (последние 7 дней):**\n"
    today = datetime.datetime.now()
    for i in range(6, -1, -1):
        date = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        count = stats["daily_activity"].get(date, 0)
        bar = "█" * min(count // 2, 20) if count > 0 else "·"
        text += f"{date[5:]} : {bar} {count} 👤\n"
    
    text += "\n🏆 **Топ-5 активных пользователей:**\n"
    sorted_users = sorted(stats["users"].items(), key=lambda x: sum(x[1].get("actions", {}).values()), reverse=True)[:5]
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        name, username = get_user_info(int(user_id))
        total_actions = sum(user_data.get("actions", {}).values())
        text += f"{i}. {username} - {total_actions} действий\n"
    
    text += "\n🎯 **Достижения:**\n"
    for achievement in ACHIEVEMENTS:
        if str(achievement["count"]) in stats["achievements"]:
            text += f"🏅 {achievement['count']} пользователей - ДОСТИГНУТО! ({stats['achievements'][str(achievement['count'])][:10]})\n"
        else:
            if achievement["count"] > total_users:
                text += f"⏳ {achievement['count']} пользователей - Осталось {achievement['count'] - total_users}\n"
    
    bot.reply_to(message, text, parse_mode="Markdown")

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
        f"🎶 {song}\n\n"
        f"🎤 *Слушай и наслаждайся!*",
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

@bot.callback_query_handler(func=lambda call
