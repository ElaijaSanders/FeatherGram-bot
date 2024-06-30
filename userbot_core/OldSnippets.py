'''@app.on_message(filters.command('a', prefixes=['.', ',', '/']) & filters.me)
def a(_, msg):
	for member in app.get_chat_members(''):
		try:
			idd = member.user.id
			ti = f'.info {idd}'
			msgeg = app.send_message('me', ti)
			info(_, msgeg)
		except Exception as e:
			pass
		t.sleep(5)
		print(member)


@app.on_message(filters.command('json', prefixes='.') & filters.me)
def message_json(_, msg):
	s = str(msg)
	print(s)
	msg.edit(s)

app.send_message('me', f'<a href="tg://user?id={msg.reply_to_message.from_user.id}">permalink</a>')
	print(app.get_users("me"))


@app.on_message(filters.command('all_chats', prefixes='.') & filters.me)
def send_chats(_, msg):
	chats = []
	msg.edit('Начинаем сбор чатов...')
	for dialog in app.get_dialogs():
		print(dialog.chat.title or dialog.chat.first_name, dialog.chat.id, sep='\n', end='\n')
		chats.append(dialog.chat)
	msg.edit(len(chats))


@app.on_message(filters.command("type", prefixes=".") & filters.me)
def type_method(_, msg):
	orig_text = msg.text.split(".type ", maxsplit=1)[1]
	text = orig_text
	tbp = ""  # to be printed
	typing_symbol = "▒"

	while tbp != orig_text:
		try:
			msg.edit(tbp + typing_symbol)
			sleep(0.05)

			tbp = tbp + text[0]
			text = text[1:]

			msg.edit(tbp)
			sleep(0.05)

		except FloodWait as e:
			sleep(e.value)
'''