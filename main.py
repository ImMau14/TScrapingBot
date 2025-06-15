import os, json, logging, datetime
from dotenv import load_dotenv
from quart import Quart, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from modules.utils import sanitize_markdown_v1
from modules.utils import divide_and_send
from modules.utils import validate_command
from modules.dolar_scraper import get_dolar_values
from modules.gemini import Gemini
from modules.database import get_history
from modules.database import register_user_and_chat
from supabase import create_client

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = Quart(__name__)
bot_app = (Application.builder().token(TELEGRAM_TOKEN).build())
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

gemini = Gemini(GEMINI_TOKEN, "chat")
DB = create_client(SUPABASE_URL, SUPABASE_KEY)

with open("./data/messages.json", "r", encoding="utf-8") as f:
	MESSAGE_DATA = json.load(f)

@validate_command("start")
async def start(update, context, message):
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
	await message.reply_text(MESSAGE_DATA["start"], parse_mode=ParseMode.MARKDOWN)

@validate_command("ping")
async def ping(update, context, message):
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
	await message.reply_text(MESSAGE_DATA["ping"], parse_mode=ParseMode.MARKDOWN)

@validate_command("help")
async def help(update, context, message):
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
	await message.reply_text('\n'.join(MESSAGE_DATA["help"]), parse_mode=ParseMode.MARKDOWN)

@validate_command("dolar")
async def dolar(update, context, message):
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
	try:
		result = await get_dolar_values()
		if "error" in result:
			await message.reply_text(f'*Error:* `{result["error"]}`\n_Details:_ `{result["details"]}`', parse_mode=ParseMode.MARKDOWN_V2)
			return

		response = MESSAGE_DATA["dolar"].format(
			dolar_bcv=str(result["dolar-bcv"]).replace('.', ','),
			dolar_par=str(result["dolar-par"]).replace('.', ','),
			dolar_pro=str(result["dolar-pro"]).replace('.', ',')
		)

		await message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)
	except Exception as e:
		logging.error(f"/dolar: {str(e)}")
		await message.reply_text(f"*Error:* `{str(e)}`", parse_mode=ParseMode.MARKDOWN_V2)

@validate_command("ask")
async def ask(update, context, message):
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
	try:
		photo_url = None
		if message.photo:
			photo_url = (await context.bot.get_file(message.photo[-1].file_id)).file_path
			text = message.caption
		else:
			text = message.text

		if not text:
			return await message.reply_text("Empty message...")

		bot_username = (await context.bot.get_me()).username

		if text.startswith(("/ask", f"/ask@{bot_username}")):
			user_query = text.split(' ', 1)[1] if len(text.split()) > 1 else None
			if not user_query:
				return await message.reply_text( "Use: /ask _<your question>_", parse_mode=ParseMode.MARKDOWN)

		elif message.chat.type == "private":
			user_query = text

		if not user_query or not user_query.strip():
			return await message.reply_text("I cannot respond to an empty query.")

		user_id, chat_id, lang = register_user_and_chat(
			message.from_user.id,
			user_query,
			message.from_user.username,
			message.chat.id,
			message.chat.type,
			DB,
			gemini
		)

		history = get_history(DB, user_id, chat_id)

		prompt_parts = [f"Respond only in {lang} (not bilingual):\n\n{user_query}"]
		if history:
			prompt_parts.append(f"\n\n{history}")

		bot_response = gemini.ask(prompt="".join(prompt_parts), photoUrl=photo_url if photo_url else None)
	
		data = {
			"user_id": user_id,
			"chat_id": chat_id,
			"msg": user_query,
			"datetime": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z"),
			"ia_response": sanitize_markdown_v1(bot_response)
		}

		await divide_and_send(data["ia_response"], message, ParseMode.MARKDOWN)
		response = DB.table("Messages").insert(data).execute()
	except Exception as e:
		logging.error(f"/ask: {str(e)}")
		await message.reply_text(f"Error: `{str(e)}`", parse_mode=ParseMode.MARKDOWN)

@validate_command("reset")
async def reset(update, context, message):
	await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")
	try:
		chat_data = DB.table("Chats").select("chat_id").eq("chat_tg_id", message.chat.id).execute()
		if not chat_data.data:
			return await message.reply_text("Not data for this chat.", parse_mode=ParseMode.MARKDOWN)

		chat_id_db = chat_data.data[0]["chat_id"]

		user_data = DB.table("Users").select("user_id").eq("tg_id", message.from_user.id).execute()
		if not user_data.data:
			return await message.reply_text("User not found.", parse_mode=ParseMode.MARKDOWN)

		user_id = user_data.data[0]["user_id"]

		update_response = DB.table("Messages").update({"is_cleared": True}) \
			.eq("chat_id", chat_id_db) \
			.eq("user_id", user_id) \
			.eq("is_cleared", False) \
			.execute()

		if not update_response.data:
			return await message.reply_text("The history chat is already reset.", parse_mode=ParseMode.MARKDOWN)

		await message.reply_text("The history chat has been reset.", parse_mode=ParseMode.MARKDOWN)

	except Exception as e:
		logging.error(f"/reset: {str(e)}")
		await message.reply_text(f"*Critical Error*\n\n{str(e)}", parse_mode=ParseMode.MARKDOWN)

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("ping", ping))
bot_app.add_handler(CommandHandler("help", help))
bot_app.add_handler(CommandHandler("dolar", dolar))
bot_app.add_handler(CommandHandler("ask", ask))
bot_app.add_handler(CommandHandler("reset", reset))

@app.route("/", methods=["GET"])
async def health_check():
	return "OK", 200

@app.route("/webhook", methods=["POST"])
async def webhook():
	data = await request.get_json(force=True)
	update = Update.de_json(data, bot_app.bot)
	await bot_app.process_update(update)
	return "OK", 200