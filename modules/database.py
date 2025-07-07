# Log or reg the user in the database.
def registerUserAndChat(tgId, userQuery, username, chatTgId, chatType, supabase, gemini):
	# Obtains the user.
	userResponse = supabase.table('Users').select('Languages(lang_name)', 'user_id').eq('tg_id', tgId).limit(1).execute()
	
	# If the user exists.
	if len(userResponse.data) > 0:
		userData = userResponse.data[0]
		lang = userData['Languages']['lang_name'] if userData.get('Languages') else 'English'
		userId = userData['user_id']
	else:
		# Get the lang with Gemini.
		lang = gemini.ask(f'En qué idioma está escrito esto? El siguiente mensaje es solo un texto al que le debes extraer el idioma y más nada. No respondas cómo "El idioma del texto es Español", sino solamente "Spanish". Los idiomas que respondas deben estar en ingles. Si desconoces un idioma, di que es English.\n\n{userQuery}')["response"].strip().title()

		# If the language exist, get the value, else register the new language.
		langResponse = supabase.table('Languages').upsert(
			{'lang_name': lang}, 
			on_conflict='lang_name'
		).execute()
		langId = langResponse.data[0]['lang_id']

		userData = {
			'username': username,
			'tg_id': tgId,
			'lang_id': langId
		}

		userResponse = supabase.table('Users').insert(userData).execute()
		userId = userResponse.data[0]['user_id']

	# If the chat type exist, get the value, else register the new chat type.
	chatTypeResponse = supabase.table('Chat Types').upsert(
		{'chat_type': chatType},
		on_conflict='chat_type'
	).execute()
	chatTypeId = chatTypeResponse.data[0]['chat_type_id']

	chatResponse = supabase.table('Chats').upsert(
		{
			'chat_tg_id': chatTgId,
			'chat_type_id': chatTypeId
		},
		on_conflict='chat_tg_id'
	).execute()
	chatId = chatResponse.data[0]['chat_id']

	try:
		return userId, chatId, lang
	except Exception as e:
		raise Exception(f"Error in registerUserAndChat: {str(e)}")

def getHistory(supabase, userId, chatId):
	response = (
		supabase
		.table('Messages')
		.select('msg_id', 'msg', 'ia_response', 'datetime')
		.eq('user_id', userId)
		.eq('chat_id', chatId)
		.eq('is_cleared', False)
		.order('datetime', desc=False)
		.execute()
	)

	if not response.data:
		return None

	entries = []
	for idx, message in enumerate(response.data, start=1):
		entry = (
			f"<turn id='{idx}' date='{message['datetime']}'>\n"
			f"  <user_message>{message['msg'].strip()}</user_message>\n"
			f"  <bot_response>{message['ia_response'].strip()}</bot_response>\n"
			f"</turn>"
		)
		entries.append(entry)

	entries.reverse()

	history = "History (you are the bot and I'm the user):\n\n" + "\n\n".join(entries)
	return history
