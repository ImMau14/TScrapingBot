import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import telebot
from scraper.dolar_scraper import getDolarValues

# ========== Configuración inicial ===========
load_dotenv()
app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
COMMAND_LIST = """Commands

/ping - Ping command.
/help - Show all commands.
/dolar - Show the dolar prices in Bs.
"""

# ========== Handlers ==========
@bot.message_handler(commands=['ping', f'start@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def start(message):
	bot.reply_to(message, "I'm here!")

@bot.message_handler(commands=['help', f'help@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def help(message):
	bot.reply_to(message, COMMAND_LIST)

@bot.message_handler(commands=['dolar', f'dolar@{BOT_NAME}'])
def handle_dolar(message):
	try:
		result = getDolarValues()
		if 'error' in result:
			bot.reply_to(
				message,
				f"*Error:* `{result['error']}`\n_Details:_ `{result['details']}`",
				parse_mode="MarkdownV2"
			)
			return

		response = (
			"🔥 *Current Dollar Prices*\n\n"
			f"🏦 *Cen:* *{result['dolar-bcv']}* Bs\\.\n"
			f"📈 *Par:* *{result['dolar-par']}* Bs\\.\n"
			f"📊 *Avg:* *{result['dolar-pro']}* Bs\\.\n"
		)

		bot.reply_to(message, response, parse_mode="MarkdownV2")

	except Exception as e:
		bot.reply_to(message, f"*Exception:* `{str(e)}`", parse_mode="MarkdownV2")

# ========== Rutas Flask ==========
@app.route('/')
def health_check():
	return "🤖 Bot activo", 200

@app.route('/webhook', methods=['POST'])
def webhook():
	if request.headers.get('content-type') == 'application/json':
		json_data = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_data)
		bot.process_new_updates([update])
		return ''
	return 'Tipo de contenido inválido', 403

# ========== Punto de entrada ==========
if __name__ == '__main__':
	if os.environ.get('HOSTING'):
		from waitress import serve
		bot.remove_webhook()
		bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
		serve(app, host='0.0.0.0', port=8080)
	else:
		bot.delete_webhook()
		bot.infinity_polling()