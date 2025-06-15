from functools import wraps, lru_cache
import re

# This function determines if the command is valid
def is_command(command, bot_username, message):
	if message.photo:
		text = message.caption
	else:
		text = message.text

	if not text:
		return False

	parts = text.strip().split(' ', 1)
	if not parts:
		return False

	base_command = parts[0]
	group_command = f"/{command}@{bot_username}"
	private_command = f"/{command}"

	return (
		((base_command == group_command) and (message.chat.type != "private")) or 
		((base_command == private_command) and (message.chat.type == "private"))
	)

@lru_cache(maxsize=1)
async def get_bot_username(context):
	bot_info = await context.bot.get_me()
	return bot_info.username

# Validate_command decorator
def validate_command(command_name):
	def decorator(handler_func):
		@wraps(handler_func)
		async def wrapper(update, context, *args, **kwargs):
			message = update.effective_message
			if not message:
				return
			bot_username = await get_bot_username(context)
			if not is_command(command_name, bot_username, message):
				return
			return await handler_func(update, context, message, *args, **kwargs)
		return wrapper
	return decorator

# Function to sanitize the MarkdownV1.
def sanitize_markdown_v1(text):
	masks = []
	def make_mask(match):
		masks.append(match.group(0))
		return f"__MASK{len(masks)-1}__"

	text = re.sub(r'```[\s\S]*?```', make_mask, text)
	text = re.sub(r'`[^`\n]+`', make_mask, text)
	text = re.sub(r'\[([^\]]+)\]\(([^)\s]+(?:\s+"[^"]*")?)\)', make_mask, text)
	text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)

	for delim in ('*', '_', '`', '[', ']'):
		if text.count(delim) % 2 == 1:
			text = text.replace(delim, '\\' + delim)

	for i, original in enumerate(masks):
		text = text.replace(f"__MASK{i}__", original)

	text = re.sub(r'(```[\s\S]*?```)\n{2}', r'\1\n', text)

	return text

# Function to split the text in diferents chunks.
def splitText(text, max_length=4096):
	chunks = []
	while len(text) > max_length:
		split_index = text.rfind('\n', 0, max_length)
		if split_index == -1:
			split_index = max_length
		chunks.append(text[:split_index])
		text = text[split_index:]
	chunks.append(text)
	return chunks

# Function to send the diferents chunks.
async def divide_and_send(text, message, parse):
	if len(text) >= 5000:
		chunks = splitText(text)
		for i, chunk in enumerate(chunks):
			await message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
	else:
		await message.reply_text(text, parse_mode=parse)

def handleError(bot, gemini, error, message):
	try:
		prompt = "Explica este error brevemente. Es para depuración, así que minimiza la información para proteger los datos. Recuerda que eres un bot de Telegram con Gemini, desplegado en Render. Responde como un compilador: (Error: mensaje): {error}"
		errorExplanation = gemini.ask(prompt.format(error=error))
		errorMsg = sanitizeMarkdownV1(errorExplanation)
		bot.reply_to(message, errorMsg, parse_mode="Markdown")

	except Exception as e:
		raise Exception(f"*Critical error*: `{str(e)}`")