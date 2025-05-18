# Log or reg the user in the database
def registerUserAndChat(tgId, userQuery, username, chatTgId, chatType, supabase, gemini):
	response = DB.table('Users').select('Languages(lang_name)', 'user_id').eq('tg_id', tgId).limit(1).execute()

	if len(response.data) > 0:
		lang = response.data[0]['Languages']['lang_name']
		userId = response.data[0]['user_id']
	else:
		lang = gemini.ask(f'En qué idioma está escrito esto? El siguiente mensaje es solo un texto al que le debes extraer el idioma y más nada. No respondas cómo "El idioma del texto es Español", sino solamente "Spanish". Los idiomas que respondas deben estar en ingles. Si desconoces un idioma, di que es English.\n\n{userQuery}')

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

	return userId, chatId, lang

# Returns the user history
def getHistory(supabase, userId, chatId):
    response = supabase.table('Messages').select('msg', 'ia_response').eq('user_id', userId).eq('chat_id', chatId).eq('is_cleared', False).execute()

    history = None
    if len(response.data) > 0:
        entries = []
        for message in response.data:
            entry = f"User: {message['msg'].strip()}\n\nBot: {message['ia_response'].strip()}"
            entries.append(entry)

        history = "History (you are the bot and I'm the user):\n\n" + "\n\n".join(entries)
    
    return history