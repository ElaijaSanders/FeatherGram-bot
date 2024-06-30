from pyrogram import Client
import platform

system_info = platform.uname()

api_id = 00000000  # айди и хэш -- значения, необходимые для регистрации кастомного клиента в системе тг
api_hash = "hashhashhashhashhashhashhashhash"  # уникальные для каждого клиента, брать с https://my.telegram.org/auth
app = Client("FeatherGram-bot", api_id, api_hash,
             device_model=system_info.node,
             app_version="0.0.10",
             system_version=system_info.system + " " + system_info.release
             )

