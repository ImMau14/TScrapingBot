# Log or reg the user in the database
def registerUserAndChat(tgId, userQuery, username, chatTgId, chatType, supabase, gemini):
	userResponse = DB.table('Users').select('Languages(lang_name)', 'user_id').eq('tg_id', tgId).limit(1).execute()
	
	if len(userResponse.data) > 0:
		userData = userResponse.data[0]
		lang = userData['Languages']['lang_name'] if userData.get('Languages') else 'English'
		userId = userData['user_id']
	else:
		lang = gemini.ask(f'...').strip().title()

		langResponse = DB.table('Languages').upsert(
			{'lang_name': lang}, 
			on_conflict='lang_name'
		).execute()
		langId = langResponse.data[0]['lang_id']

		userData = {
			'username': username,
			'tg_id': tgId,
			'lang_id': langId
		}

		userResponse = DB.table('Users').insert(userData).execute()
		userId = userResponse.data[0]['user_id']

	chatTypeResponse = DB.table('Chat Types').upsert(
		{'chat_type': chatType},
		on_conflict='chat_type'
	).execute()
	chatTypeId = chatTypeResponse.data[0]['chat_type_id']
	
	chatResponse = DB.table('Chats').upsert(
		{
			'chat_tg_id': chatTgId,
			'chat_type_id': chatTypeId
		},
		on_conflict='chat_tg_id'
	).execute()
	chatId = chatResponse.data[0]['chat_id']
	
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