import telebot
from telebot import types
import json
import os
from flask import Flask, request, jsonify
import threading

TOKEN = "8647866146:AAEchlfSvhJkH9He6lP_1NdyXN-MjYm66XM"
ADMIN_ID = "ТВОЙ_TELEGRAM_ID"
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
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("🎵 ПЕРЕЙТИ К ОПРОСУ", url=SITE_URL))
    bot.send_message(
        message.chat.id,
        "🎵 **ASPER X · YOUR TOP**\n\n"
        "Перейди по ссылке, пройди опрос и получи свой топ-90!\n\n"
        "После завершения нажми **«Вернуться в бота»**, чтобы сохранить результат.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

app = Flask(__name__)

@app.route('/save_results', methods=['POST'])
def save_results():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        top_90 = data.get('top_90', [])

        if not top_90:
            return jsonify({"status": "error", "message": "No top_90"}), 400

        user_results = load_json(USER_RESULTS_FILE)
        user_results[user_id] = top_90
        save_json(USER_RESULTS_FILE, user_results)

        try:
            text = "🏆 **ТВОЙ ТОП-90**\n\n"
            for i, (song, score) in enumerate(top_90[:10], 1):
                text += f"{i}. {song} — {score} ⭐\n"
            if len(top_90) > 10:
                text += f"\n... и ещё {len(top_90) - 10} песен"
            bot.send_message(user_id, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка отправки пользователю: {e}")

        try:
            text = f"📊 **Новый топ-3 от {user_id}**\n\n"
            for i, (song, score) in enumerate(top_90[:3], 1):
                text += f"{i}. {song} — {score} ⭐\n"
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")

        global_ranking = load_json(GLOBAL_RANKING_FILE)
        points = [5, 3, 1]
        for idx, (song, _) in enumerate(top_90[:3]):
            if song in global_ranking:
                global_ranking[song] += points[idx]
            else:
                global_ranking[song] = points[idx]
        save_json(GLOBAL_RANKING_FILE, global_ranking)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bot.message_handler(commands=['ranking'])
def ranking(message):
    data = load_json(GLOBAL_RANKING_FILE)
    if not data:
        bot.send_message(message.chat.id, "📊 Пока нет голосов. Будь первым!")
        return

    sorted_songs = sorted(data.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 **ОБЩИЙ РЕЙТИНГ**\n\n"
    current_place = 1
    for i, (song, score) in enumerate(sorted_songs, 1):
        if i > 1 and sorted_songs[i-1][1] != sorted_songs[i-2][1]:
            current_place = i
        medal = "🥇" if current_place == 1 else "🥈" if current_place == 2 else "🥉" if current_place == 3 else f"{current_place}."
        text += f"{medal} {song} — {score} ⭐\n"
        if i >= 20:
            break

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Бот и сервер запущены...")
    bot.polling(none_stop=True)
