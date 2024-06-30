from userbot_core.init_and_start.init import app
from pyrogram.errors import FloodWait
import asyncio
import json

from pyrogram import enums, types
from typing import Union, List, Optional
from datetime import datetime

SYMBOLS = 4096
MAX_LSEP = 15
MAX_ESEP = 30
MAX_DELTA = 100


class Plain:
	def bdivide_to_parts(self, v: str):
		while len(v) > 0:
			if len(v) < SYMBOLS:
				self.carry.append(v)
				break
			else:
				pos_n = v.find("\n", 0, SYMBOLS)
				pos_e = v.find(self.end_sep, 0, SYMBOLS)
				pos_l = v.find(self.list_sep, 0, SYMBOLS)
				if 0 <= SYMBOLS-1 - pos_e <= MAX_DELTA:
					self.carry.append(v[:pos_e])
					v = v[pos_e+len(self.end_sep):]
				elif 0 <= SYMBOLS-1 - pos_l <= MAX_DELTA:
					self.carry.append(v[:pos_l])
					v = v[pos_l+len(self.list_sep):]
				elif 0 <= SYMBOLS-1 - pos_n <= MAX_DELTA:
					self.carry.append(v[:pos_n])
					v = v[pos_n+1:]
				else:
					self.carry.append(v[:SYMBOLS])
					v = v[SYMBOLS:]
		self.__update_partiality()

	def divide_to_parts(self, v: str, dividable: bool = True):
		if dividable:
			while len(v) > 0:
				if len(v) < SYMBOLS:
					self.carry.append(v)
					break
				else:
					self.carry.append(v[:SYMBOLS])
					v = v[SYMBOLS:]
		else:
			self.carry.append(
				v if len(v) < SYMBOLS else v[:SYMBOLS]
			)
		self.__update_partiality()

	def __init__(self, value, end_sep: str = "", dividable: bool = True, _list_sep: str = "\n", _outer: bool = False):
		self.list_sep = _list_sep
		self.end_sep = end_sep
		self.carry = []
		self.is_one_part = True

		value = str(value)
		if _outer:
			self.bdivide_to_parts(value)
		else:
			self.divide_to_parts(value, dividable)

		if len(self.carry[-1]) <= SYMBOLS - len(self.end_sep):
			self.carry[-1] = self.carry[-1] + self.end_sep

	@property
	def end_sep(self):
		return self.__end_sep

	@end_sep.setter
	def end_sep(self, sep: str):
		if type(sep) != str:
			raise TypeError
		elif len(sep) > MAX_ESEP:
			raise ValueError
		self.__end_sep = sep

	@property
	def is_one_part(self):
		return self.__is_one_part

	@is_one_part.setter
	def is_one_part(self, val: bool):
		if type(val) != bool:
			raise TypeError
		self.__is_one_part = val

	def __update_partiality(self):
		res = bool(len(self.carry) == 1)
		self.__is_one_part = res
		return res

	@property
	def list_sep(self):
		return self.__list_sep

	@list_sep.setter
	def list_sep(self, sep: str):
		if type(sep) != str:
			raise TypeError
		elif len(sep) > MAX_LSEP:
			raise ValueError
		self.__list_sep = sep

	def __str__(self):
		rep = {
			"is_one_part": self.is_one_part,
			"carry": self.carry,
			"list_sep": self.list_sep,
			"end_sep": self.end_sep
		}
		return json.dumps(rep, indent=4)


class Block(Plain):
	def __init__(self, value, list_sep: str = "\n", end_sep: str = "\n\n"):
		if type(value) not in (list, tuple, map, set):
			value = str(value)
		else:
			for i in range(len(value)):
				value[i] = str(value[i])
			value = list_sep.join(value)
		super().__init__(value, end_sep=end_sep, _list_sep=list_sep, _outer=True)

		'''if type(value) == str:
			self.pdivide_to_parts(value)
		elif type(value) in (list, tuple, map, set):
			for i in range(len(value)):
				value[i] = str(value[i])
			value = list_sep.join(value)
			self.pdivide_to_parts(value)
		else:
			value = str(value)
			self.pdivide_to_parts(value)'''


class CSend:
	@staticmethod
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

	@staticmethod
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
			result = CSend.safe_send(
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

	@staticmethod
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

	def __init__(self, queue=None, seq_mode: str = ""):
		self.seq_mode = seq_mode
		if queue is None:
			self.queue = []

	@property
	def seq_mode(self):
		return self.__seq_mode

	@seq_mode.setter
	def seq_mode(self, mode: str = ""):
		self.__seq_mode = mode

