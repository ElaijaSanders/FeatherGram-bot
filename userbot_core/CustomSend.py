from userbot_core.init_and_start.init import app
from pyrogram.errors import FloodWait
from pyrogram import enums, types
from typing import Union, List, Optional

import asyncio
from datetime import datetime


def safe_send(
		chat_id: Union[int, str],
		text: str,
		parse_mode: Optional["enums.ParseMode"] = None,
		entities: List["types.MessageEntity"] = None,
		disable_web_page_preview: bool = None,
		disable_notification: bool = None,
		reply_to_message_id: int = None,
		schedule_date: datetime = None,
		protect_content: bool = None,
		reply_markup: Union[
			"types.InlineKeyboardMarkup",
			"types.ReplyKeyboardMarkup",
			"types.ReplyKeyboardRemove",
			"types.ForceReply"
		] = None
):
	result = None
	try:
		result = app.send_message(
			chat_id,
			text,
			parse_mode,
			entities,
			disable_web_page_preview,
			disable_notification,
			reply_to_message_id,
			schedule_date,
			protect_content,
			reply_markup
		)
	except FloodWait as FW:
		asyncio.sleep(FW.value)
		result = app.send_message(
			chat_id,
			text,
			parse_mode,
			entities,
			disable_web_page_preview,
			disable_notification,
			reply_to_message_id,
			schedule_date,
			protect_content,
			reply_markup
		)
	finally:
		return result


def send_big_text(
		chat_id: Union[int, str],
		text: str,
		parse_mode: Optional["enums.ParseMode"] = None,
		entities: List["types.MessageEntity"] = None,
		disable_web_page_preview: bool = None,
		disable_notification: bool = None,
		reply_to_message_id: int = None,
		schedule_date: datetime = None,
		protect_content: bool = None,
		reply_markup: Union[
			"types.InlineKeyboardMarkup",
			"types.ReplyKeyboardMarkup",
			"types.ReplyKeyboardRemove",
			"types.ForceReply"
		] = None
):
	parts = [text[i:i + 4096] for i in range(0, len(text), 4096)]
	result_messages = []
	for part in parts:
		result = safe_send(
			chat_id,
			part,
			parse_mode,
			entities,
			disable_web_page_preview,
			disable_notification,
			reply_to_message_id,
			schedule_date,
			protect_content,
			reply_markup
		)
		if result:
			result_messages.append(result)
	return result_messages


def safe_edit(
		chat_id: Union[int, str],
		message_id: int,
		text: str,
		parse_mode: Optional["enums.ParseMode"] = None,
		entities: List["types.MessageEntity"] = None,
		disable_web_page_preview: bool = None,
		reply_markup: "types.InlineKeyboardMarkup" = None
):
	result = None
	try:
		result = app.edit_message_text(
			chat_id,
			message_id,
			text,
			parse_mode,
			entities,
			disable_web_page_preview,
			reply_markup
		)
	except FloodWait as FW:
		asyncio.sleep(FW.value)
		result = app.edit_message_text(
			chat_id,
			message_id,
			text,
			parse_mode,
			entities,
			disable_web_page_preview,
			reply_markup
		)

	finally:
		return result
