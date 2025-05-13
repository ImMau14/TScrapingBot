import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import telebot
from modules.dolar_scraper import getDolarValues
from modules.gemini import Gemini
import re

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

def split_text(text, max_length=4096):
	chunks = []
	while len(text) > max_length:
		idx = text.rfind('\n', 0, max_length)
		if idx == -1:
			idx = max_length
		chunks.append(text[:idx])
		text = text[idx:]
	chunks.append(text)
	return chunks

@bot.message_handler(commands=['ask', f'ask@{BOT_NAME}'], content_types=['text', 'photo'])
def ask(message):
	# Solo respondemos cuando es comando /ask o en chat privado
	if message.text.startswith('/ask@' + BOT_NAME) or message.chat.type == 'private':
		chat_id = message.chat.id

		try:
			# 1) Extraer prompt de texto (caption o después del comando)
			prompt = None
			if message.photo:
				# si viene foto, toma caption como prompt
				prompt = message.caption or ""
			else:
				parts = message.text.split(' ', 1)
				prompt = parts[1] if len(parts) > 1 else None

			if not prompt and not message.photo:
				return bot.reply_to(message, "❓ Usa `/ask <tu pregunta>` o envía una foto con caption.")

			# 2) Descargar bytes de la foto (si existe)
			image_bytes = None
			if message.photo:
				file_id   = message.photo[-1].file_id
				file_info = bot.get_file(file_id)
				image_bytes = bot.download_file(file_info.file_path)

			# 3) Llamar a Gemini
			g = Gemini(GEMINI_TOKEN, 'chat')
			respuesta = g.ask(prompt, image_bytes)

			# 4) Sanitizar y fragmentar la respuesta en trozos de ≤4096 chars
			texto = sanitize_markdown_v1(respuesta)
			for i, trozo in enumerate(split_text(texto)):
				if i == 0:
					bot.reply_to(message, trozo, parse_mode="Markdown")
				else:
					bot.send_message(chat_id, trozo, parse_mode="Markdown")

		except Exception as e:
			# Mismo estilo de error que tenías
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