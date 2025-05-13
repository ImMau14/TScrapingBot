import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import telebot
from modules.dolar_scraper import getDolarValues
from modules.gemini import Gemini
from modules.page_scraper import obtainPageText
import re

load_dotenv()
app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
SCRAPEDO_TOKEN = os.getenv('SCRAPEDO_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
COMMAND_LIST = """*Commands*

/ping - Ping command
/help - Show this command list
/dolar - Show the current dollar prices in Bs
/ask <query> - Ask to Gemini 2.0
/search <url> <query> - Search in the URL
"""

def sanitize_markdown_v1(text: str) -> str:
	# Enmascarar bloques de código, inline y enlaces
	masks = []
	def make_mask(match):
		masks.append(match.group(0))
		return f"__MASK{len(masks)-1}__"

	# Triple backticks (bloque de código)
	text = re.sub(r'```[\s\S]*?```', make_mask, text)
	# Inline code
	text = re.sub(r'`[^`\n]+`', make_mask, text)
	# Enlaces Markdown
	text = re.sub(r'\[([^\]]+)\]\(([^)\s]+(?:\s+"[^"]*")?)\)', make_mask, text)

	# Justificación izquierda en el resto
	text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)

	# Escapar delimitadores desbalanceados fuera de máscaras
	for delim in ('*', '_', '`', '[', ']'):
		if text.count(delim) % 2 == 1:
			text = text.replace(delim, '\\' + delim)

	# Restaurar máscaras
	for i, original in enumerate(masks):
		text = text.replace(f"__MASK{i}__", original)

	# Quitar línea en blanco extra tras cada bloque de código
	text = re.sub(r'(```[\s\S]*?```)\n{2}', r'\1\n', text)

	return text

@bot.message_handler(commands=['ping', f'ping@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def ping(message):
	if message.text.startswith('/ping@' + BOT_NAME) or message.chat.type == 'private':
		bot.reply_to(message, "I'm here! TScrapingBot v1.1 online!")

@bot.message_handler(commands=['help', f'help@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def help(message):
	if message.text.startswith('/help@' + BOT_NAME) or message.chat.type == 'private':
		bot.reply_to(message, COMMAND_LIST, parse_mode="Markdown")

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
		chat_id = message.chat.id
		try:
			user_query = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None

			if not user_query:
				return bot.reply_to(message)

			g = Gemini(GEMINI_TOKEN, 'chat')
			r = g.ask(user_query)
			r = sanitize_markdown_v1(r)

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
					bot.send_message(chat_id, chunk, parse_mode="Markdown")

		except Exception as e:
			bot.reply_to(message, f"*Error*: `{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['search', f'search@{BOT_NAME}'])
def search(message):
	if message.text.startswith('/search@' + BOT_NAME) or message.chat.type == 'private':
		chat_id = message.chat.id
		try:
			msg = message.text.split(' ', 2)
			userURL = message.text.split(' ', 2)[1] if len(message.text.split()) > 1 else None
			user_query = message.text.split(' ', 2)[2] if len(message.text.split()) > 1 else None

			url = f"http://api.scrape.do?token={SCRAPEDO_TOKEN}&url={userURL}"

			if not user_query:
				return bot.reply_to(message)

			g = Gemini(GEMINI_TOKEN, 'chat')
			r = g.ask(f"{user_query} \n\n{obtainPageText(url)} \n\nPage URL: {userURL}")
			r = sanitize_markdown_v1(r)

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
					bot.send_message(chat_id, chunk, parse_mode="Markdown")

		except Exception as e:
			bot.reply_to(message, f"*Error*: `{e}`", parse_mode="Markdown")

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

if __name__ == '__main__':
	if os.environ.get('HOSTING'):
		from waitress import serve
		bot.remove_webhook()
		bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
		serve(app, host='0.0.0.0', port=8080)
	else:
		bot.delete_webhook()
		bot.infinity_polling()