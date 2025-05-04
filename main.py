import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import telebot
from modules.dolar_scraper import getDolarValues
from modules.gemini import Gemini

# ========== Configuración inicial ===========
load_dotenv()
app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
COMMAND_LIST = """Commands

/ping - Ping command
/help - Show the command list
/dolar - Show the current dollar prices in Bs
/ask - Ask to Gemini 2.0
"""

# ========== Handlers ==========
@bot.message_handler(commands=['ping', f'ping@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def ping(message):
	if message.text.startswith('/ping@' + BOT_NAME) or message.chat.type == 'private':
		bot.reply_to(message, "I'm here!")

@bot.message_handler(commands=['help', f'help@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def help(message):
	if message.text.startswith('/help@' + BOT_NAME) or message.chat.type == 'private':
		bot.reply_to(message, COMMAND_LIST)

@bot.message_handler(commands=['dolar', f'dolar@{BOT_NAME}'])
def dolar(message):
	if message.text.startswith('/dolar@' + BOT_NAME) or message.chat.type == 'private':
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
				f"🏦 *Cen:* *{str(result['dolar-bcv']).replace('.', ',')}* Bs\\.\n"
				f"📈 *Par:* *{str(result['dolar-par']).replace('.', ',')}* Bs\\.\n"
				f"📊 *Avg:* *{str(result['dolar-pro']).replace('.', ',')}* Bs\\.\n"
			)

			bot.reply_to(message, response, parse_mode="MarkdownV2")

		except Exception as e:
			bot.reply_to(message, f"*Critical Error:* `{str(e)}`", parse_mode="MarkdownV2")

@bot.message_handler(commands=['ask', f'ask@{BOT_NAME}'])
def ask(message):
	if message.text.startswith('/ask@' + BOT_NAME) or message.chat.type == 'private':
		try:
			user_query = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None

			if not user_query:
				return bot.reply_to(message)

			g = Gemini(GEMINI_TOKEN, 'chat')
			r = g.ask(user_query)

			# Función para dividir el texto
			def split_text(text, max_length=4096):
				chunks = []
				while len(text) > max_length:
					split_index = text.rfind('\n', 0, max_length)  # Busca último salto de línea
					if split_index == -1:
						split_index = max_length  # Si no hay salto, corta al límite
					chunks.append(text[:split_index])
					text = text[split_index:]
				chunks.append(text)
				return chunks

			# Dividir y enviar
			chunks = split_text(r)
			for i, chunk in enumerate(chunks):
				if i == 0:
					bot.reply_to(message, chunk, parse_mode="Markdown")
				else:
					bot.reply_to(message, chunk, parse_mode="Markdown")

		except Exception as e:
			bot.reply_to(message, f"*Error*: `{e}`", parse_mode="Markdown")

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