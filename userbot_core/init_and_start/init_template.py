from pyrogram import Client

api_id = 00000000  # айди и хэш -- значения, необходимые для регистрации кастомного клиента в системе тг
api_hash = "hashhashhashhashhashhashhashhash"  # уникальные для каждого клиента, брать с https://my.telegram.org/auth
app = Client("FeatherGram-bot", api_id, api_hash)
