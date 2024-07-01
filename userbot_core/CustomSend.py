from userbot_core.init_and_start.init import app
from pyrogram.errors import FloodWait
from pyrogram import enums, types
from typing import Union, List, Optional

import asyncio
from datetime import datetime

CHARACTERS_LIMIT = 4096  # max number of characters in one message
AUTO_SPLIT_MAX_CHARACTERS = 150  # max number of characters searched through in split.auto mode
SPLIT_MODES = (  # all possible values of split_mode parameter
    "exact_limit",  # Split into parts of exactly CHARACTERS_LIMIT characters
    "eol",  # Split at the nearest newline character to the limit
    "word_sep",  # Split at the nearest to the limit word separator (one from WORD_SEPARATORS)
    "auto"  # If a newline or word separator is found within AUTO_SPLIT_MAX_CHARACTERS characters, split there;
    # otherwise, split at exactly CHARACTERS_LIMIT characters
)
WORD_SEPARATORS = (" ", "\n", "\r", ".", ",", "!", "?", ">", "/", "\\", "'", "\"", "]", ")", "}")


def split(big_text: str, split_mode: str = "auto") -> list[str]:
    """
    Splits the text provided in big_text into parts of CHARACTERS_LIMIT or fewer characters,
    using the splitting method specified in split_mode.

    :param big_text:
        the text that needs to be split into parts
    :param split_mode:
        the mode of splitting the text;
        must be one of the values in ("exact_limit", "eol", "word_sep", "auto")
    :return:
        a list of strings - parts of the original text obtained by
        splitting big_text using the method, specified in split_mode

    All possible values of split_mode:
    * "exact_limit" - splits into parts of exactly CHARACTERS_LIMIT characters;
    * "eol" - searches to the left of the assumed boundary at CHARACTERS_LIMIT for the nearest newline character '\n',
        and splits at that point;
    * "word_sep" - searches to the left of the assumed boundary at CHARACTERS_LIMIT for
        the nearest word-separating character (one of the characters in WORD_SEPARATORS), and splits at that point;
    * "auto" - searches within the nearest AUTO_SPLIT_MAX_CHARACTERS characters to the left of the assumed boundary at
        CHARACTERS_LIMIT for the nearest word-separating character (one of the characters in WORD_SEPARATORS)
        or the nearest newline character and splits at that point,
        and if neither a newline nor a word separator is found within the nearest AUTO_SPLIT_MAX_CHARACTERS characters,
        splits that part as "exact_limit".
    """
    if split_mode not in SPLIT_MODES:  # check for incorrect split_mode value
        raise ValueError("split_mode must be one of the values in SPLIT_MODES!")
    if big_text == "":
        raise ValueError("Can't send empty message!")
    parts = []
    if split_mode == "exact_limit":
        # dividing into parts of exactly CHARACTERS_LIMIT characters
        parts = [big_text[i:i + CHARACTERS_LIMIT] for i in range(0, len(big_text), CHARACTERS_LIMIT)]
        return parts
    while big_text != "":  # while there are some parts left
        if len(big_text) <= CHARACTERS_LIMIT:  # if it is the last part
            parts.append(big_text)
            break
        for current_char in range(min(CHARACTERS_LIMIT - 1, len(big_text)), 0, -1):
            # searching to the left for newline or word separator
            if split_mode in ("eol", "auto") and big_text[current_char] == "\n":
                parts.append(big_text[0:current_char + 1])  # adding part, that ends on current_char
                big_text = big_text[current_char + 1:]  # subtracting that part from all text
                break
            if split_mode in ("word_sep", "auto") and big_text[current_char] in WORD_SEPARATORS:
                parts.append(big_text[0:current_char + 1])  # adding part, that ends on current_char
                big_text = big_text[current_char + 1:]  # subtracting that part from all text
                break

            is_nothing_found = \
                (split_mode == "auto" and
                 current_char == CHARACTERS_LIMIT - 1 - AUTO_SPLIT_MAX_CHARACTERS) \
                or current_char == CHARACTERS_LIMIT // 2
            if is_nothing_found:
                # if auto mode searched through AUTO_SPLIT_MAX_CHARACTERS characters, or eol/word_sep mode searched
                # through half of the part, and nothing found,
                parts.append(big_text[0:CHARACTERS_LIMIT])  # adding part with length CHARACTERS_LIMIT
                big_text = big_text[CHARACTERS_LIMIT:]  # subtracting that part from all text
                break
    return parts


def safe_send(
        chat_id: Union[int, str],
        text: str,
        split_mode: Optional[str] = "auto",
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
    """
    Send text messages of any length by splitting them into blocks of 4096 characters, handles FloodWait errors.

    :param chat_id:
        Unique identifier (int) or username (str) of the target chat.
        For your personal cloud (Saved Messages) you can simply use "me" or "self".
        For a contact that exists in your Telegram address book you can use his phone number (str)
    :param text:
        Text of the message to be sent
    :param split_mode:
        the mode of splitting the text;
        must be one of the values in ("exact_limit", "eol", "word_sep", "auto")
    :param parse_mode:
        By default, texts are parsed using both Markdown and HTML styles.
        You can combine both syntaxes together
    :param entities:
        List of special entities that appear in message text, which can be specified instead of *parse_mode*
    :param disable_web_page_preview:
        Disables link previews for links in this message
    :param disable_notification:
        Sends the message silently.
        Users will receive a notification with no sound
    :param reply_to_message_id:
        If the message is a reply, ID of the original message
    :param schedule_date:
        Date when the message will be automatically sent
    :param protect_content:
        Protects the contents of the sent message from forwarding and saving
    :param reply_markup:
        Additional interface options. An object for an inline keyboard, custom reply keyboard,
        instructions to remove reply keyboard or to force a reply from the user.
    :return:
        On success, the list of all sent text messages is returned.
    """
    parts = split(text, split_mode)
    result_messages = []
    for index, part in enumerate(parts):
        result = None
        try:
            result = app.send_message(
                chat_id,
                part,
                parse_mode,
                entities,
                disable_web_page_preview,
                disable_notification,
                reply_to_message_id if index == 0 else result_messages[0].id,
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
                reply_to_message_id if index == 0 else result_messages[0].id,
                schedule_date,
                protect_content,
                reply_markup
            )
        except BaseException as e:
            print(e)
        finally:
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
