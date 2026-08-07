import telebot
from telebot import types
import json
import os
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
ADMIN_ID = "832018497"
bot = telebot.TeleBot(TOKEN)

SITE_URL = "https://tinvafla.github.io/AsperX_Your_Top_Songs_Site/"

GLOBAL_RANKING_FILE = "global_ranking.json"
USER_RESULTS_FILE = "user_results.json"

user_states = {}

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
    if user_id_str in user_results:
        user_data = user_results[user_id_str]
        if isinstance(user_data, dict):
            return user_data.get("exclude_from_ranking", False)
        else:
            return False
    return False

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

def send_new_menu(chat_id, user_id):
    keyboard = get_menu_keyboard(user_id)
    bot.send_message(
        chat_id,
        "Выбери действие:",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
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

@bot.callback_query_handler(func=lambda call: call.data == "story")
def story(call):
    bot.answer_callback_query(call.id)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✉️ НАПИСАТЬ АВТОРУ", callback_data="write_author"),
        types.InlineKeyboardButton("🔙 ВЕРНУТЬСЯ НАЗАД", callback_data="back_to_menu")
    )
    
    bot.edit_message_text(
        "📖 **ИСТОРИЯ СОЗДАНИЯ**\n\n"
        "Привет! 👋\n\n"
        "Я tinvafla, или вафелька — как тебе удобнее. И я та самая, кто собрал этого бота на голом энтузиазме.\n\n"
        "Всё началось с того, что я очень люблю разбирать вещи по полочкам. Особенно музыку. Особенно Asper X. Я искала платформу, где можно было бы сравнивать треки, составлять личный топ, видеть, что выбирают другие — и не нашла. Ничего. Совсем.\n\n"
        "Тогда я подумала: «А почему бы не сделать это самой?»\n\n"
        "У меня не было опыта. Вообще. Ни строчки кода до этого. Но были нейросети, пара свободных вечеров и огромное желание. Так появился этот бот и сайт. С нуля, с идеей, с багами и с любовью.\n\n"
        "Собрала 90 песен Asper X — ровно столько, сколько нашла. Если что-то пропустила — пиши, исправлюсь! Здесь только основной проект, без RetroElektro и других ответвлений, хотя они тоже крутые и, надеюсь, до них руки дойдут тоже.\n\n"
        "В мечтах — добавить короткие превью к песням (секунд по 5), чтобы можно было вспомнить трек, если название не говорит само за себя. Но тут сложность с авторскими правами, поэтому пока не готова. Если этот бот найдёт отклик у аудитории — я вернусь к этой идее.\n\n"
        "Версия 1.0 — тестовая. Проверяю, заходит ли такой формат, и очень переживаю, чтобы обновления не сломали уже собранные результаты 🤞\n\n"
        "Всё это сделано из искренней любви к творчеству группы Asper X и Тима Эрны. Гиперфиксации нейроотличных умных людей творят чудеса. Очень жду 27 октября, чтобы выразить свою любовь вживую 🫶\n\n"
        "Спасибо, что вы здесь. Что проходите опрос. Что помогаете делать этот рейтинг живым.\n\n"
        "Связаться со мной можно через функционал бота — я читаю всё 💬",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    bot.answer_callback_query(call.id)
    send_new_menu(call.message.chat.id, call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_ranking")
def toggle_ranking(call):
    user_id = call.from_user.id
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    
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
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    global_ranking = load_json(GLOBAL_RANKING_FILE)
    points = [5, 3, 1]
    
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
        
        if isinstance(user_results[user_id_str], dict):
            user_results[user_id_str]["exclude_from_ranking"] = False
        else:
            user_results[user_id_str] = {"top_90": user_results[user_id_str], "exclude_from_ranking": False}
        
        save_json(GLOBAL_RANKING_FILE, global_ranking)
        save_json(USER_RESULTS_FILE, user_results)
    
    bot.answer_callback_query(call.id, "✅ Готово!")
    bot.edit_message_text(
        "✅ Твои результаты снова учитываются в общем рейтинге.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    
    try:
        user = bot.get_chat(user_id)
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"
        username = f"@{user.username}" if user.username else "не установлен"
        
        msg = f"🔔 Пользователь снова учитывается в общем рейтинге\n\n"
        msg += f"👤 Имя: {name}\n"
        msg += f"🔗 Ник: {username}\n"
        msg += f"🆔 ID: {user_id}\n\n"
        msg += "Его баллы добавлены в общий рейтинг."
        
        bot.send_message(ADMIN_ID, msg)
    except:
        pass
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_exclude")
def confirm_exclude(call):
    user_id = call.from_user.id
    user_id_str = str(user_id)
    user_results = load_json(USER_RESULTS_FILE)
    global_ranking = load_json(GLOBAL_RANKING_FILE)
    points = [5, 3, 1]
    
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
        
        if isinstance(user_results[user_id_str], dict):
            user_results[user_id_str]["exclude_from_ranking"] = True
        else:
            user_results[user_id_str] = {"top_90": user_results[user_id_str], "exclude_from_ranking": True}
        
        save_json(GLOBAL_RANKING_FILE, global_ranking)
        save_json(USER_RESULTS_FILE, user_results)
    
    bot.answer_callback_query(call.id, "✅ Готово!")
    bot.edit_message_text(
        "✅ Твои результаты исключены из общего рейтинга.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    
    try:
        user = bot.get_chat(user_id)
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"
        username = f"@{user.username}" if user.username else "не установлен"
        
        msg = f"🔔 Пользователь исключил себя из общего рейтинга\n\n"
        msg += f"👤 Имя: {name}\n"
        msg += f"🔗 Ник: {username}\n"
        msg += f"🆔 ID: {user_id}\n\n"
        msg += "Его баллы удалены из общего рейтинга."
        
        bot.send_message(ADMIN_ID, msg)
    except:
        pass
    
    send_new_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_toggle")
def cancel_toggle(call):
    bot.answer_callback_query(call.id, "❌ Отменено")
    send_new_menu(call.message.chat.id, call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "my_results")
def my_results(call):
    user_id = call.from_user.id
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
        else:
            bot.edit_message_text(
                "❌ **У тебя нет сохранённых результатов!**\n\nПерейди по ссылке и пройди опрос, чтобы получить свой топ.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
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

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == "waiting_for_author_message":
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
        
        print("👤 user_id:", user_id)
        print("📊 Количество песен в top_90:", len(top_90))

        if not top_90:
            print("❌ top_90 пустой!")
            return jsonify({"status": "error", "message": "No top_90"}), 400

        user_results = load_json(USER_RESULTS_FILE)
        global_ranking = load_json(GLOBAL_RANKING_FILE)
        points = [5, 3, 1]
        
        old_exclude = False
        
        if user_id in user_results:
            user_data = user_results[user_id]
            if isinstance(user_data, dict):
                old_top_90 = user_data.get("top_90", [])
                old_exclude = user_data.get("exclude_from_ranking", False)
            else:
                old_top_90 = user_data
                old_exclude = False
            
            if old_top_90 and len(old_top_90) >= 3:
                old_top_3 = old_top_90[:3]
                for idx, (song, _) in enumerate(old_top_3):
                    if song in global_ranking:
                        global_ranking[song] -= points[idx]
                        if global_ranking[song] <= 0:
                            del global_ranking[song]
        
        user_results[user_id] = {"top_90": top_90, "exclude_from_ranking": old_exclude}
        save_json(USER_RESULTS_FILE, user_results)
        print("✅ Результаты сохранены для:", user_id)

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
            text += f"🆔 ID: {user_id}\n\n"
            for i, (song, score) in enumerate(top_90[:3], 1):
                text += f"{i}. {song}\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton("📩 ОТВЕТИТЬ", callback_data=f"reply_{user_id}"))
            
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown", reply_markup=keyboard)
            print("✅ Топ-3 отправлен админу")
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")

        if not old_exclude:
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
