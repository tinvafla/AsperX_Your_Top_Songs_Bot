import telebot
from telebot import types
import json
import threading
from supabase import create_client, Client

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
ADMIN_ID = "832018497"

SUPABASE_URL = "https://gbfdpkudkxkqqtykjbok.supabase.co"
SUPABASE_KEY = "sb_secret_2nc1X5n9hqfs-CqkafxgdQ_xSH-Ym1Q"

bot = telebot.TeleBot(TOKEN)
SITE_URL = "https://tinvafla.github.io/AsperX_Your_Top_Songs_Site/"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== ФУНКЦИИ РАБОТЫ С БАЗОЙ =====
def get_user_results(user_id):
    response = supabase.table("users").select("*").eq("user_id", str(user_id)).execute()
    return response.data[0] if response.data else None

def get_all_users():
    response = supabase.table("users").select("*").execute()
    return response.data

def save_user_results(user_id, top_90, exclude=False):
    data = {
        "user_id": str(user_id),
        "top_90": json.dumps(top_90, ensure_ascii=False),
        "exclude_from_ranking": exclude
    }
    supabase.table("users").upsert(data).execute()

def get_global_ranking():
    response = supabase.table("global_ranking").select("data").eq("id", 1).execute()
    return response.data[0].get("data", {}) if response.data else {}

def save_global_ranking(data):
    supabase.table("global_ranking").upsert({"id": 1, "data": data}).execute()

def get_user_exclude_status(user_id):
    result = get_user_results(user_id)
    return result.get("exclude_from_ranking", False) if result else False

# ===== КЛАВИАТУРА =====
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
    
    keyboard.add(types.InlineKeyboardButton("📖 ИСТОРИЯ СОЗДАНИЯ", callback_data="story"))
    keyboard.add(types.InlineKeyboardButton("✉️ НАПИСАТЬ АВТОРУ", callback_data="write_author"))
    
    return keyboard

def send_menu(chat_id, user_id):
    bot.send_message(chat_id, "Выбери действие:", reply_markup=get_menu_keyboard(user_id))

# ===== КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        "🎵 <b>ASPER X · YOUR TOP SONGS</b>\n\n"
        "Перейди по ссылке, пройди опрос и получи свой топ!\n\n"
        "⏳ Тест займёт ~3–5 минут.\n"
        "💡 Можно перепройти опрос — старые результаты заменятся.\n\n"
        "🛠️ Сделано на энтузиазме, без опыта, но с любовью.\n"
        "<blockquote>У меня, может, и нет мозгов, господа, но у меня есть идея.</blockquote>\n"
        "💬 Обратная связь приветствуется!",
        parse_mode="HTML"
    )
    send_menu(message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)

    if call.data == "my_results":
        user = get_user_results(user_id)
        if not user:
            bot.edit_message_text("❌ Ты ещё не проходил опрос!", call.message.chat.id, call.message.message_id)
        else:
            top_90 = json.loads(user.get("top_90", "[]"))
            if not top_90:
                bot.edit_message_text("❌ Нет результатов!", call.message.chat.id, call.message.message_id)
            else:
                text = "🏆 **ТВОЙ ТОП**\n\n"
                for i, (song, score) in enumerate(top_90[:20], 1):
                    text += f"{i}. {song}\n"
                if len(top_90) > 20:
                    text += f"\n... и ещё {len(top_90) - 20} песен"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        send_menu(call.message.chat.id, user_id)
        return

    if call.data == "show_ranking":
        ranking = get_global_ranking()
        if not ranking:
            bot.edit_message_text("📊 Пока нет голосов.", call.message.chat.id, call.message.message_id)
        else:
            sorted_songs = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
            text = "🏆 **ОБЩИЙ РЕЙТИНГ**\n\n"
            for i, (song, score) in enumerate(sorted_songs[:20], 1):
                text += f"{i}. {song} — {score}⭐\n"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        send_menu(call.message.chat.id, user_id)
        return

    if call.data == "toggle_ranking":
        user = get_user_results(user_id)
        if not user:
            bot.answer_callback_query(call.id, "Сначала пройди опрос!")
            return
        top_90 = json.loads(user.get("top_90", "[]"))
        exclude = user.get("exclude_from_ranking", False)
        new_exclude = not exclude
        save_user_results(user_id, top_90, new_exclude)

        ranking = get_global_ranking()
        points = [5, 3, 1]
        
        if exclude:
            # Добавляем баллы
            for idx, (song, _) in enumerate(top_90[:3]):
                ranking[song] = ranking.get(song, 0) + points[idx]
            save_global_ranking(ranking)
            bot.edit_message_text("✅ Ты снова в общем рейтинге.", call.message.chat.id, call.message.message_id)
        else:
            # Удаляем баллы
            for idx, (song, _) in enumerate(top_90[:3]):
                if song in ranking:
                    ranking[song] -= points[idx]
                    if ranking[song] <= 0:
                        del ranking[song]
            save_global_ranking(ranking)
            bot.edit_message_text("✅ Ты исключён из общего рейтинга.", call.message.chat.id, call.message.message_id)
        
        send_menu(call.message.chat.id, user_id)
        return

    if call.data == "story":
        bot.edit_message_text(
            "📖 **ИСТОРИЯ СОЗДАНИЯ**\n\n"
            "Привет! Я tinvafla, или вафелька.\n"
            "Этот бот родился из любви к музыке Asper X.\n"
            "Сделано на коленке, с душой и без опыта.\n"
            "Любая обратная связь — в радость!",
            call.message.chat.id, call.message.message_id, parse_mode="Markdown"
        )
        send_menu(call.message.chat.id, user_id)
        return

    if call.data == "write_author":
        bot.edit_message_text("📝 Напиши своё сообщение автору. Я передам!", call.message.chat.id, call.message.message_id)
        user_states[user_id] = "waiting_for_author_message"
        return

user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if user_states.get(user_id) == "waiting_for_author_message":
        bot.send_message(ADMIN_ID, f"✉️ Сообщение от @{message.from_user.username or user_id}:\n{message.text}")
        bot.reply_to(message, "✅ Передано автору!")
        del user_states[user_id]
        send_menu(message.chat.id, user_id)

# ===== ЗАПУСК =====
if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.remove_webhook()
    bot.polling(none_stop=True)
