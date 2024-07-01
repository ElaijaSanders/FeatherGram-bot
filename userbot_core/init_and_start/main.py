from pyrogram import *
from pyrogram import types
import re
from time import sleep
from userbot_core.CustomSend import safe_send, safe_edit
from userbot_core.init_and_start.init import app
import platform
import subprocess


@app.on_message(
    filters.command(
        ['battery', 'batery', 'btry', 'acumulator', 'accumulator', 'accumulat', 'acumulat', 'батарея', 'батарейка'],
        prefixes=['.', ',', '/', '']
    ) &
    filters.user("me")
)
def battery(_, msg: types.Message):
    try:
        result = subprocess.check_output(['termux-battery-status'])
        result = result.decode("utf-8", errors="replace")
        print(result)
        msg.edit(result)
    except FileNotFoundError:
        msg.edit(
            "❌**Невозможно получить доступ к батарее!**❌\n\n"
            "Убедитесь, что хост -- Termux с установленным Termux:API"
        )


@app.on_message(
    filters.command(
        ['info', 'inf', 'this', 'инфо', 'инфа', 'инф', 'зис', 'інфо', 'інфа', 'інф', 'зіс'],
        prefixes=['.', ',', '/', '']
    ) &
    filters.user("me")
)
def info(_, msg: types.Message):
    def create_info(target: types.User, pref=None):
        def check_mutual_contact(check_user: types.User):
            wasnt_contact = not check_user.is_contact
            if wasnt_contact:
                app.add_contact(check_user.id, "UB Temp: is_mutual")
            result = check_user.is_mutual_contact
            if wasnt_contact:
                app.delete_contacts(check_user.id)
            return result

        def gen_origin_mention(check_user: types.User):
            if check_user.is_contact:
                contact_first = (">No name<" if check_user.first_name is None else check_user.first_name)
                contact_last = ("" if check_user.last_name is None else check_user.last_name)
                deleted_as = app.delete_contacts(check_user.id)
                origin_first = (">No name<" if deleted_as.first_name is None else deleted_as.first_name)
                origin_last = ("" if deleted_as.last_name is None else deleted_as.last_name)
                app.add_contact(check_user.id, contact_first, contact_last)
                res = check_user.mention(
                    (">No name<" if origin_first is None else origin_first) +
                    (' ' + origin_last if origin_last is not None else '')
                )
            else:
                res = check_user.mention(
                    (">No name<" if check_user.first_name is None else check_user.first_name) +
                    (' ' + check_user.last_name if check_user.last_name is not None else ''))
            return res

        side_visible_name = gen_origin_mention(target)

        final_info = f'**{pref}name:** ' + side_visible_name + '\n'
        if target.is_contact and str(msg.text).find('+contact') != -1:
            contact_name = target.mention(
                (">No name<" if target.first_name is None else target.first_name) +
                ("" if target.last_name is None else (' ' + target.last_name))
            )
            final_info = final_info + f'**{pref}saved as**: ' + contact_name + '\n'
        final_info = final_info + f'**{pref}ID**: `{target.id}`\n' \
            f'**{pref}user**: @{target.username}\n' \
            f'**{pref}phone**: `+{target.phone_number}`\n' \
            f'**{pref}has me in contact**: {check_mutual_contact(target)}\n'
        return final_info

    passports = [[], []]

    def passp_setter(some_user: types.User, pref: str):
        if some_user.id not in passports[1]:
            passports[1].append(some_user.id)
            passports[0].append(create_info(some_user, pref))

    query = str(msg.text)
    try:  # todo: send_info
        msg.edit("Processing...\n")
    except Exception:
        app.send_message(msg.chat.id, "Processing...\n", disable_notification=True, reply_to_message_id=msg.id)

    if msg.reply_to_message is not None:  # сборка инфы с пересланного, отвеченного и текущего
        repl_msg = msg.reply_to_message
        if repl_msg.forward_from is not None:
            passp_setter(repl_msg.forward_from, 'Fwd ')
        passp_setter(repl_msg.from_user, 'Repl ')
        query = query + ' ' + str(repl_msg.text)

    unexp_symbs = r"[^0-9A-Za-z _@\.]"  # убирает симвоолы, которых не может быть в айди или юзернейме
    query = re.sub(unexp_symbs, ' ', query)
    query = query.split()

    allowable_identifier = r"(@[0-9A-Za-z_\.]{5,32})|(^[1-9][0-9]{0,20})"
    for user in query:
        if re.match(allowable_identifier, user) is None:
            query.remove(user)
        else:
            try:
                app.get_users(user)
            except Exception:
                query.remove(user)
            else:
                passp_setter(app.get_users(user), 'Search ')
            finally:
                continue

    if len(passports[0]) == 0:
        app.send_message(msg.chat.id, "Nothing found! :(\n", disable_notification=True, reply_to_message_id=msg.id)
    else:
        text = "Here what i found:\n"
        iterator = 0
        while len(passports[0]) > 0:
            text = text + passports[0][0] + '\n'
            passports[0].pop(0)
            iterator += 1
            if iterator % 5 == 0 or len(passports[0]) == 0:
                app.send_message(
                    msg.chat.id,
                    text,
                    disable_notification=True,
                    reply_to_message_id=msg.id
                )
                text = ''
        try:
            msg.delete()
        except Exception:
            pass


@app.on_message(
    filters.command(
        ['json'],
        prefixes=['.', ',', '/', '']
    ) &
    filters.user("me")
)
def json(_, msg: types.Message):
    print(msg)
    msg.edit("Done!")
    sleep(5)
    msg.delete()


@app.on_message(
    filters.command(
        ['top_chat_active'],
        prefixes=['.', ',', '/', '']
    ) &
    filters.user("me")
)
def a(_, msg: types.Message):
    safe_edit(msg.chat.id, msg.id, "🟡 Начинаем подсчёт сообщений...")
    sleep(0.5)
    counter = {}
    for person in app.get_chat_members(msg.chat.id):
        linked_name = \
            f'<a href="tg://user?id={person.user.id}">' + \
            (person.user.first_name if person.user.first_name else ">No name<") + \
            ((' ' + person.user.last_name) if person.user.last_name else "") + \
            '</a>'
        counter[person.user.id] = [linked_name, 0]

    started_flag = False
    max_id = 0
    old_progress = -1
    for message in app.get_chat_history(msg.chat.id):
        if not started_flag:
            max_id = message.id
            started_flag = True

        have_processed = max_id-message.id
        new_progress = 100*have_processed//max_id
        print(f"\rcounting messages: {message.id}    {have_processed}/{max_id}  ({new_progress}%)", end='')
        if new_progress != old_progress:
            simply_progress = round(new_progress/5)*5
            text_to_show = \
                f"🌀Считаем сообщения...\n\n" \
                f"{have_processed}/{max_id}  ({new_progress}%)\n" \
                "[ " + "█ "*(simply_progress//10)+"▄ "*((simply_progress % 10)//5) + "░ "*((100-simply_progress)//10)+"]"
            safe_edit(msg.chat.id, msg.id, text_to_show)
            old_progress = new_progress

        try:
            counter[message.from_user.id][1] += 1
        except KeyError:
            leaved_user = app.get_users(message.from_user.id)
            name = "[left] " + \
                f'<a href="tg://user?id={leaved_user.id}">' + \
                (leaved_user.first_name if leaved_user.first_name else ">No name<") + \
                ((' ' + leaved_user.last_name) if leaved_user.last_name else "") + \
                '</a>'
            counter[message.from_user.id] = [name, 1]
        except AttributeError:
            continue

    print("\n\n")
    counter = list(counter.items())

    def take_value(elem):
        return elem[1][1]
    counter.sort(key=take_value, reverse=True)

    final_text = f"🏆ТОП АКТИВНИХ В ЧАТІ '{msg.chat.first_name or msg.chat.title}'🏆:\n\n"
    for index in range(len(counter)):
        final_text = final_text + f"{index+1})  " + str(counter[index][1][0]) + f" :  {counter[index][1][1]}\n"

    safe_edit(msg.chat.id, msg.id, final_text)


@app.on_message(
    filters.command(
        ['edit'],
        prefixes=['.', ',', '/', '']
    ) &
    filters.user("me")
)
def test_edit(_, message: types.Message):
    safe_edit(
        message.chat.id,
        message.id,
        "editing..."
    )
    result = safe_edit(
        message.chat.id,
        message.reply_to_message_id,
        "editing test"
    )
    print(result)

app.run()


'''
@app.on_disconnect()
def disconnected(self):
    now = dt.datetime.now()
    print(f"{now.day}.{now.month}.{now.day} | {now.hour}:{now.minute}:{now.second}.{now.microsecond}\n    restarting...")
    app.restart()
    
'''

