import re

# Function to sanitize the MarkdownV1.
def sanitizeMarkdownV1(text):
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
def divideAndSend(text, bot, message):
	if len(text) >= 4096:
		chunks = splitText(text)
		for i, chunk in enumerate(chunks):
			bot.reply_to(message, chunk, parse_mode="Markdown")
	else:
		bot.reply_to(message, text, parse_mode="Markdown")

def handleError(bot, gemini, error, message):
	try:
		prompt = "Explica este error brevemente. Es para depuración, así que minimiza la información para proteger los datos. Recuerda que eres un bot de Telegram con Gemini, desplegado en Render. Responde como un compilador: (Error: mensaje): {error}"
		errorExplanation = gemini.ask(prompt.format(error=error))
		errorMsg = sanitizeMarkdownV1(errorExplanation["response"])
		bot.reply_to(message, errorMsg, parse_mode="Markdown")

	except Exception as e:
		raise Exception(f"*Critical error*: `{str(e)}`")

def chatAction(action, bot, message):
	bot.send_chat_action(
		message.chat.id,
		action=action,
		message_thread_id=message.message_thread_id if message.chat.is_forum else None
	)