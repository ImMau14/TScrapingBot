import telebot, os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from modules.gemini import Gemini
from modules.dolar_scraper import getDolarValues
from modules.page_scraper import obtainPageText
from modules.utils import sanitizeMarkdownV1
from modules.utils import divideAndSend
from supabase import create_client
import datetime
import json

with open("./data/messages.json", "r", encoding="utf-8") as f:
	MESSAGE_DATA = json.load(f)

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
SCRAPEDO_TOKEN = os.getenv('SCRAPEDO_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
gemini = Gemini(GEMINI_TOKEN, 'chat')
DB = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

@bot.message_handler(commands=['start', f'start@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def start(message):
	if message.text.startswith('/start@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		bot.reply_to(message, MESSAGE_DATA['start'])

@bot.message_handler(commands=['ping', f'ping@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def ping(message):
	if message.text.startswith('/ping@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		bot.reply_to(message, MESSAGE_DATA['ping'])

@bot.message_handler(commands=['help', f'help@{BOT_NAME}'], chat_types=["private", "group", "supergroup"])
def help(message):
	if message.text.startswith('/help@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		bot.reply_to(message, '\n'.join(MESSAGE_DATA['commands']), parse_mode="Markdown")

@bot.message_handler(commands=['dolar', f'dolar@{BOT_NAME}'])
def dolar(message):
	if message.text.startswith('/dolar@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		try:
			result = getDolarValues()
			if 'error' in result:
				bot.reply_to(
					message,
					f"*Error:* `{result['error']}`\n_Details:_ `{result['details']}`",
					parse_mode="MarkdownV2"
				)
				return

			response = MESSAGE_DATA['dolar'].format(
				dolar_bcv=str(result['dolar-bcv']).replace('.', ','),
				dolar_par=str(result['dolar-par']).replace('.', ','),
				dolar_pro=str(result['dolar-pro']).replace('.', ',')
			)

			bot.reply_to(message, response, parse_mode="MarkdownV2")

		except Exception as e:
			bot.reply_to(message, f"*Error:* `{str(e)}`", parse_mode="MarkdownV2")

@bot.message_handler(commands=['ask', f'ask@{BOT_NAME}'])
@bot.message_handler(chat_types=["private"], func=lambda message: message.text is not None and not message.text.startswith('/'))
def ask(message):
	if message.text.startswith('/ask@' + BOT_NAME) or message.chat.type == 'private':
		try:
			chatTgId = message.chat.id
			tgId = message.from_user.id
			chatType = message.chat.type

			bot.send_chat_action(chatTgId, 'typing')

			if message.text.startswith(('/ask', f'/ask@{BOT_NAME}')):
				user_query = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
				if not user_query:
					return bot.reply_to(message, "📝 Use: /ask _your question_", parse_mode="Markdown")
			elif chatType == 'private':
				user_query = message.text

			if not user_query or not user_query.strip():
				return bot.reply_to(message, "I cannot respond to an empty query.")

			response = DB.table('Users').select('Languages(lang_name)', 'user_id').eq('tg_id', tgId).limit(1).execute()

			if len(response.data) > 0:
				lang = response.data[0]['Languages']['lang_name']
				userId = response.data[0]['user_id']
			else:
				username = message.from_user.username
				lang = gemini.ask(f'¿En qué idioma está escrito esto? El siguiente mensaje es solo un texto al que le debes extraer el idioma y más nada. No respondas cómo "El idioma del texto es Español", sino solamente "Spanish". Los idiomas que respondas deben estar en ingles. Si desconoces un idioma, di que es English.\n\n{user_query}')

				data = {
					'username': username,
					'tg_id': tgId
				}

				response = DB.table('Languages').select('lang_id').eq('lang_name', lang).limit(1).execute()

				if len(response.data) > 0:
					data['lang_id'] = response.data[0]['lang_id']
				else:
					response = DB.table('Languages').insert({'lang_name': lang}).execute()
					data['lang_id'] = response.data[0]['lang_id']

				response = DB.table('Users').insert(data).execute()
				userId = response.data[0]['user_id']

			response = DB.table('Chats').select('chat_id').eq('chat_tg_id', chatTgId).limit(1).execute()

			if len(response.data) > 0:
				chatId = response.data[0]['chat_id']
			else:
				data = {
					'chat_tg_id': chatTgId
				}

				response = DB.table('Chat Types').select('chat_type_id').eq('chat_type', chatType).execute()

				if len(response.data) > 0:
					data['chat_type_id'] = response.data[0]['chat_type_id']
				else:
					response = DB.table('Chat Types').insert({'chat_type': chatType}).execute()
					data['chat_type_id'] = response.data[0]['chat_type_id']
				
				response = DB.table('Chats').insert(data).execute()
				chatId = response.data[0]['chat_id']

			response = DB.table('Messages').select('msg', 'ia_response').eq('is_cleared', False).execute()

			history = None
			if len(response.data) > 0:
				history = f"History (you are the bot and I'm the user):\n\n"
				for count, messages in enumerate(response.data, start=1):
					history += f"User: {messages['msg'].strip()}\n\nBot: {messages['ia_response'].strip()}{'\n\n' if not count == len(response.data) else ''}"

			botResponse = gemini.ask(f"Respond only in {lang} (not bilingual):\n\n{user_query}{f'\n\n{history}' if history else ''}")

			data = {
				'user_id': userId,
				'chat_id': chatId,
				'msg': user_query,
				'datetime': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z'),
				'ia_response': sanitizeMarkdownV1(botResponse)
			}

			divideAndSend(data['ia_response'], bot, message)
			response = DB.table('Messages').insert(data).execute()

		except Exception as e:
			try:
				error_msg = sanitizeMarkdownV1(gemini.ask(f'Explica este error brevemente. Es para depuración, así que minimiza la información para proteger los datos. Recuerda que eres un bot de Telegram con Gemini, desplegado en Render. Responde como un compilador: "Error: mensaje": {e}'))
				bot.reply_to(message, error_msg, parse_mode="Markdown")

			except Exception as f:
				bot.reply_to(message, f"*Critical error*: `{f}`", parse_mode="Markdown")

@bot.message_handler(commands=['search', f'search@{BOT_NAME}'])
def search(message):
	if message.text.startswith('/search@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		try:
			msg = message.text.split(' ', 2)
			userURL = message.text.split(' ', 2)[1] if len(message.text.split()) > 1 else None
			user_query = message.text.split(' ', 2)[2] if len(message.text.split()) > 1 else None

			if not userURL or not user_query:
				return bot.reply_to(message, "Usage: /search <url> <query>.")

			userURL = userURL.replace('&', '%26')

			if not user_query:
				return bot.reply_to(message)

			botResponse = gemini.ask(f"{user_query} \n\n{obtainPageText(userURL, SCRAPEDO_TOKEN)} \n\nPage URL: {userURL}")
			divideAndSend(sanitizeMarkdownV1(botResponse), bot, message)

		except Exception as e:
			bot.reply_to(message, f"*Error*: `{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['reset', f'reset@{BOT_NAME}'])
def reset(message):
	if message.text.startswith('/reset@' + BOT_NAME) or message.chat.type == 'private':
		bot.send_chat_action(message.chat.id, 'typing')
		try:
			chatData = DB.table('Chats').select('chat_id').eq('chat_tg_id', message.chat.id).execute()

			if len(chatData.data) == 0:
				return bot.reply_to(message, f"Not chat history.", parse_mode="Markdown")

			chatId = chatData.data[0]['chat_id']
			updateResponse = DB.table('Messages').update({'is_cleared': True}).eq('chat_id', chatId).eq('is_cleared', False).execute()

			if len(updateResponse.data) == 0:
				return bot.reply_to(message, f"This history has already been reset.", parse_mode="Markdown")

			bot.reply_to(message, f"The history for this chat has been reset.", parse_mode="Markdown")

		except Exception as e:
			try:
				error_msg = sanitizeMarkdownV1(gemini.ask(f'Explica este error brevemente. Es para depuración, así que minimiza la información para proteger los datos. Recuerda que eres un bot de Telegram con Gemini, desplegado en Render. Responde como un compilador: "Error: mensaje": {e}'))
				bot.reply_to(message, error_msg, parse_mode="Markdown")

			except Exception as f:
				bot.reply_to(message, f"*Critical error*: `{f}`", parse_mode="Markdown")


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