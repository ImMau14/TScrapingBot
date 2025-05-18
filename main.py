import telebot, os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from modules.gemini import Gemini
from modules.dolar_scraper import getDolarValues
from modules.page_scraper import obtainPageText
from modules.utils import sanitizeMarkdownV1
from modules.utils import divideAndSend
from modules.utils import handleError
from modules.database import getHistory
from modules.database import registerUserAndChat
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
			bot.send_chat_action(message.chat.id, 'typing')

			# Selecting the userQuery.
			if message.text.startswith(('/ask', f'/ask@{BOT_NAME}')):
				userQuery = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
				if not userQuery:
					return bot.reply_to(message, "Use: /ask _your question_", parse_mode="Markdown")
			elif message.chat.type == 'private':
				userQuery = message.text
			if not userQuery or not userQuery.strip():
				return bot.reply_to(message, "I cannot respond to an empty query.")

			userId, chatId, lang = registerUserAndChat(
				message.from_user.id,
				userQuery,
				message.from_user.username,
				message.chat.id,
				message.chat.type,
				DB,
				gemini
			)

			history = getHistory(DB, userId, chatId)

			promptParts = [f"Respond only in {lang} (not bilingual):\n\n{userQuery}"]
			if history:
				promptParts.append(f"\n\n{history}")

			botResponse = gemini.ask("".join(promptParts))

			data = {
				'user_id': userId,
				'chat_id': chatId,
				'msg': userQuery,
				'datetime': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z'),
				'ia_response': sanitizeMarkdownV1(botResponse)
			}

			divideAndSend(data['ia_response'], bot, message)
			response = DB.table('Messages').insert(data).execute()

		except Exception as e:
			try:
				handleError(bot, gemini, str(e), message)
			except Exception as e:
				return bot.reply_to(message, f"*Critical Error*\n\n{str(e)}", parse_mode="Markdown")

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
			# Obtain chat data
			chatData = DB.table('Chats').select('chat_id').eq('chat_tg_id', message.chat.id).execute()
			if len(chatData.data) == 0:
				return bot.reply_to(message, "Not data for this chat.", parse_mode="Markdown")
			
			chatId = chatData.data[0]['chat_id']

			# Obtain the user_id from the Users table
			userData = DB.table('Users').select('user_id').eq('user_tg_id', message.from_user.id).execute()
			if len(userData.data) == 0:
				return bot.reply_to(message, "User not found.", parse_mode="Markdown")
			user_id = userData.data[0]['user_id']

			updateResponse = DB.table('Messages').update({'is_cleared': True}).eq('chat_id', chatId).eq('user_id', user_id).eq('is_cleared', False).execute()

			if len(updateResponse.data) == 0:
				return bot.reply_to(message, "The history chat is already reset.", parse_mode="Markdown")

			bot.reply_to(message, "The history chat has been reset.", parse_mode="Markdown")

		except Exception as e:
			try:
				handleError(bot, gemini, str(e), message)
			except Exception as e:
				return bot.reply_to(message, f"*Critical Error*\n\n{str(e)}", parse_mode="Markdown")

@app.route('/')
def health_check():
	return "馃 Bot activo", 200

@app.route('/webhook', methods=['POST'])
def webhook():
	if request.headers.get('content-type') == 'application/json':
		json_data = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_data)
		bot.process_new_updates([update])
		return ''
	return 'Tipo de contenido inv谩lido', 403

if __name__ == '__main__':
	if os.environ.get('HOSTING'):
		from waitress import serve
		bot.remove_webhook()
		bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
		serve(app, host='0.0.0.0', port=8080)
	else:
		bot.delete_webhook()
		bot.infinity_polling()