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

SITE_URL = "https://asperxyourtopsongs.netlify.app/"

GLOBAL_RANKING_FILE = "global_ranking.json"
USER_RESULTS_FILE = "user_results.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎵 ПЕРЕЙТИ К ОПРОСУ", url=f"{SITE_URL}?user_id={user_id}"),
        types.InlineKeyboardButton("📊 МОИ РЕЗУЛЬТАТЫ", callback_data="my_results"),
        types.InlineKeyboardButton("🏆 ОБЩИЙ РЕЙТИНГ", callback_data="show_ranking")
    )
    bot.send_message(
        message.chat.id,
        "🎵 **ASPER X · YOUR TOP**\n\n"
        "Перейди по ссылке, пройди опрос и получи свой топ!\n\n"
        "После завершения нажми **«Вернуться в бота»** или **«Мои результаты»**, чтобы получить свой топ.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "my_results")
def my_results(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "📊 Загружаю твои результаты...")
    
    user_results = load_json(USER_RESULTS_FILE)
    user_id_str = str(user_id)
    
    if user_id_str in user_results:
        top_90 = user_results[user_id_str]
        text = "🏆 **ТВОЙ ТОП**\n\n"
        for i, (song, score) in enumerate(top_90, 1):
            text += f"{i}. {song}\n"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(
            call.message.chat.id,
            "❌ **Ты ещё не проходил опрос!**\n\n"
            "Перейди по ссылке и пройди опрос, чтобы получить свой топ.",
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "show_ranking")
def show_ranking_callback(call):
    bot.answer_callback_query(call.id)
    ranking(call.message)

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
        
        if user_id in user_results:
            old_top_90 = user_results[user_id]
            old_top_3 = old_top_90[:3]
            for idx, (song, _) in enumerate(old_top_3):
                if song in global_ranking:
                    global_ranking[song] -= points[idx]
                    if global_ranking[song] <= 0:
                        del global_ranking[song]
        
        user_results[user_id] = top_90
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
            text = f"📊 **Новый топ-3 от {user_id}**\n\n"
            for i, (song, score) in enumerate(top_90[:3], 1):
                text += f"{i}. {song}\n"
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
            print("✅ Топ-3 отправлен админу")
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")

        for idx, (song, _) in enumerate(top_90[:3]):
            if song in global_ranking:
                global_ranking[song] += points[idx]
            else:
                global_ranking[song] = points[idx]
        save_json(GLOBAL_RANKING_FILE, global_ranking)
        print("✅ Общий рейтинг обновлён")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ ОШИБКА:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@bot.message_handler(commands=['ranking'])
def ranking(message):
    data = load_json(GLOBAL_RANKING_FILE)
    if not data:
        bot.send_message(message.chat.id, "📊 Пока нет голосов. Будь первым!")
        return

    user_results = load_json(USER_RESULTS_FILE)
    voters_count = len(user_results)

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

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Бот и сервер запущены...")
    bot.polling(none_stop=True)
