#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import subprocess
import pymysql
from contextlib import closing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

adm_sessionslist = []

def parse_admin_command(update, context):
    """Parse update for admin commands."""
    if update.message.chat.type == "private":
        if update.message.text.find("/admin") == 0 or update.message.text.find("!одмин") == 0:
            pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
            with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE \'botusers\'")
                    if cursor.rowcount == 0:
                        # id | u_id | u_privs | u_name | u_fname
                        cursor.execute("CREATE TABLE botusers ( \
                                        id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                                        u_id INT, \
                                        u_privs INT, \
                                        u_name CHAR(128), \
                                        u_fname CHAR(128))")
                        cursor.execute("INSERT INTO botusers ( u_id, u_privs ) VALUES ( \'" + str(update.message.from_user.id) + "\', \'0\')")
                        if update.message.chat.username is not None:
                            cursor.execute("UPDATE botusers SET u_name = \'" + update.message.chat.username + "\' WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                        if update.message.chat.first_name is not None:
                            cursor.execute("UPDATE botusers SET u_fname = \'" + update.message.chat.first_name + "\' WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                    cursor.execute("SELECT u_privs FROM botusers WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                    if cursor.rowcount == 0:
                        cursor.execute("INSERT INTO botusers ( u_id, u_privs ) VALUES ( \'" + str(update.message.from_user.id) + "\', \'9\')")
                        if update.message.chat.username is not None:
                            cursor.execute("UPDATE botusers SET u_name = \'" + update.message.chat.username + "\' WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                        if update.message.chat.first_name is not None:
                            cursor.execute("UPDATE botusers SET u_fname = \'" + update.message.chat.first_name + "\' WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                        update.message.reply_text("Получен ранг 9")
                    else:
                        privs = str(cursor.fetchone())[1:2]
                        check_adm(update, context, privs)
                conn.commit()

def check_adm(update, context, privs):
    """Check for chats where bot is admin."""
    if int(privs) < 2:
        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE \'chat\_%\'")
                if cursor.rowcount != 0:
                    keyboard = []
                    ret = cursor.fetchall()
                    for r in ret:
                        c_id = int(str(r)[6:][:-3].replace("_","-"))
                        c_info = context.bot.get_chat(c_id)
                        if c_info["type"] != "private":
                            if context.bot.get_chat_member(c_id, context.bot.get_me()["id"])["status"] == "administrator":
                                c_data = "checkadm" + privs + " " + str(c_id)
                                keyboard.append([InlineKeyboardButton(c_info["title"], callback_data=c_data)])
                    if int(privs) < 1:
                        keyboard.append([InlineKeyboardButton("[Пользователи бота]", callback_data="admins")])
                    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('Чат:', reply_markup=reply_markup)
    else:
        update.message.reply_text("Необходим ранг < 2")

def admins_cb(update, context):
    """Manage bot admins (for owner)."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="[Пользователи бота]")
    r_msg = "ID | Ранг | Имя пользователя | Имя"
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    keyboard = []
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u_id, u_privs, u_name, u_fname FROM botusers")
            if cursor.rowcount != 0:
                ret = cursor.fetchall()
                for r in ret:
                    c_text = str(r)[1:-1].replace(","," |")
                    c_data = "adm_edituser " + c_text
                    keyboard.append([InlineKeyboardButton(c_text, callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Добавить из групп", callback_data="adm_add")])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(r_msg, reply_markup=reply_markup)

def adm_edituser_cb(update, context):
    query = update.callback_query
    query.answer()
    c_data = query.data[query.data.find(" ")+1:]
    query.edit_message_text(text=c_data)
    c_data = c_data[:c_data.find(" ")]
    keyboard = []
    c_data = "adm_rank " + c_data
    keyboard.append([InlineKeyboardButton("Изменить ранг", callback_data=c_data)])
    c_data = c_data.replace("adm_rank ", "adm_del ")
    keyboard.append([InlineKeyboardButton("Удалить", callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Действие:", reply_markup=reply_markup)

def adm_rank_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Изменить ранг")
    query.message.reply_text("Новый ранг:")
    u_id = query.data[query.data.find(" ")+1:]
    session = [query.from_user.id, u_id, "adm_rank_cb"]
    global adm_sessionslist
    adm_sessionslist.append(session)

def adm_add_cb(update, context):
    """Add bot admin."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Добавить из групп")
    keyboard = []
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE \'chat\_%\'")
            if cursor.rowcount != 0:
                l_users = []
                ret = cursor.fetchall()
                for r in ret:
                    cursor.execute("SELECT DISTINCT msg_uid, msg_user FROM " + str(r)[2:-3] + " WHERE msg_uid != \'0\'")
                    if cursor.rowcount != 0:
                        ret2 = cursor.fetchall()
                        for r2 in ret2:
                            luid = str(r2)[1:str(r2).find(",")]
                            luname = str(r2)[str(r2).find("'")+1:-2]
                            if luname.find("(") == 0:
                                luname = "None"
                            l_user = [luid, luname]
                            l_users.append(l_user)
                r_uids = []
                cursor.execute("SELECT u_id FROM botusers")
                if cursor.rowcount != 0:
                    ret = cursor.fetchall()
                    for r_uid in ret:
                        r_uids.append(str(r_uid)[1:-2])
                t_users = []
                for l_user in l_users:
                    if l_user not in t_users and l_user[0] not in r_uids:
                        t_users.append(l_user)
                for t_user in t_users:
                    b_user = str(t_user[0]) + " | " + str(t_user[1])
                    c_data = "adm_useradd " + str(t_user[0]) + " " + str(t_user[1])
                    keyboard.append([InlineKeyboardButton(b_user, callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("ID | Имя пользователя", reply_markup=reply_markup)

def adm_useradd_cb(update, context):
    query = update.callback_query
    query.answer()
    u_id = query.data[query.data.find(" ")+1:]
    u_name = u_id[u_id.find(" ")+1:]
    u_id = u_id[:u_id.find(" ")]
    e_msg = u_id + " | " + u_name
    query.edit_message_text(text=e_msg)
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO botusers ( u_id, u_privs, u_name ) VALUES ( \'" + u_id + "\', \'1\', \'" + u_name +"\' )")
        conn.commit()
    query.message.reply_text("Добавлен")

def adm_del_cb(update, context):
    """Delete bot admin."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Удалить")
    query.message.reply_text("Да/Нет?:")
    u_id = query.data[query.data.find(" ")+1:]
    session = [query.from_user.id, u_id, "adm_del_cb"]
    global adm_sessionslist
    adm_sessionslist.append(session)

def checkadm_cb(update, context):
    """Chat menu."""
    query = update.callback_query
    query.answer()
    privs = query.data[8:9]
    g_id = query.data[query.data.find(" ")+1:]
    t_act = context.bot.get_chat(g_id)["title"]
    query.edit_message_text(text=t_act)
    keyboard = []
    if int(privs) < 2:
        c_data = "af_show " + g_id
        keyboard.append([InlineKeyboardButton("Антифлуд", callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Действие:', reply_markup=reply_markup)

def af_show_cb(update, context):
    """Antiflood menu."""
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    query.edit_message_text(text="Антифлуд")
    f_secs = "60"
    f_times = "6"
    b_secs = "33"
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            chatid = "chat" + g_id.replace("-", "_")
            cursor.execute("SHOW TABLES LIKE \'floodrules\'")
            if cursor.rowcount == 0:
                # id | chat_id | flood_secs | flood_times | ban_secs
                cursor.execute("CREATE TABLE floodrules ( \
                                id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                                chat_id CHAR(64), \
                                flood_secs INT, \
                                flood_times INT, \
                                ban_secs INT)")
            cursor.execute("SELECT flood_secs, flood_times, ban_secs FROM floodrules WHERE chat_id = \'" + chatid + "\'")
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO floodrules (chat_id, flood_secs, flood_times, ban_secs) VALUES (\'" + chatid + "\', \'" + f_secs + "\', \'" + f_times + "\', \'" + b_secs + "\')")
            else:
                ret = cursor.fetchone()
                f_settings = str(ret).replace("(","").replace(")","").replace(",","")
                f_secs = f_settings[:f_settings.find(" ")]
                f_settings = f_settings[f_settings.find(" ")+1:]
                f_times = f_settings[:f_settings.find(" ")]
                f_settings = f_settings[f_settings.find(" ")+1:]
                b_secs = f_settings
    keyboard = []
    c_data = "af_f_times " + g_id
    keyboard.append([InlineKeyboardButton("после [" + f_times + "] сообщений", callback_data=c_data)])
    c_data = "af_f_secs " + g_id
    keyboard.append([InlineKeyboardButton("за [" + f_secs + "] сек", callback_data=c_data)])
    c_data = "af_b_secs " + g_id
    keyboard.append([InlineKeyboardButton("блок на [" + b_secs + "] сек", callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Изменить:', reply_markup=reply_markup)

def af_f_times_cb(update, context):
    """Open session for AF messages count."""
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_f_times_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новое количество сообщений:")

def af_f_secs_cb(update, context):
    """Open session for AF time interval."""
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_f_secs_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новый интервал времени, сек:")

def af_b_secs_cb(update, context):
    """Open session for AF restriction duration."""
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_b_secs_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новая длительность блокировки, сек (>30):")

def cancel_cb(update, context):
    """Cancel button callback."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.message.text)
    query.message.reply_text(text="Отменено.")

def check_sessions(update, context):
    """Manage and close sessions."""
    global adm_sessionslist
    for session in adm_sessionslist:
        if update.message.chat.type == "private":
            if session[0] == update.message.from_user.id:
                g_id = session[1]
                if session[2] == "af_f_times_cb":
                    if update.message.text.isdigit():
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                chatid = "chat" + g_id.replace("-", "_")
                                cursor.execute("UPDATE floodrules SET flood_times = \'" + update.message.text + "\' WHERE chat_id = \'" + chatid + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = context.bot.get_chat(g_id)["title"] + ": Количество сообщений установлено " + update.message.text
                        update.message.reply_text(t_answ)

                if session[2] == "af_f_secs_cb":
                    if update.message.text.isdigit():
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                chatid = "chat" + g_id.replace("-", "_")
                                cursor.execute("UPDATE floodrules SET flood_secs = \'" + update.message.text + "\' WHERE chat_id = \'" + chatid + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = context.bot.get_chat(g_id)["title"] + ": Интервал времени установлен " + update.message.text
                        update.message.reply_text(t_answ)

                if session[2] == "af_b_secs_cb":
                    if update.message.text.isdigit():
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                chatid = "chat" + g_id.replace("-", "_")
                                cursor.execute("UPDATE floodrules SET ban_secs = \'" + update.message.text + "\' WHERE chat_id = \'" + chatid + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = context.bot.get_chat(g_id)["title"] + ": Длительность блокировки установлена " + update.message.text
                        update.message.reply_text(t_answ)

                # if session[2] == "adm_add_cb":
                #     if update.message.text.isdigit(): #todo: additional check
                #         pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                #         pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                #         with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                #             with conn.cursor() as cursor:
                #                 cursor.execute("INSERT INTO botusers ( u_id, u_privs ) VALUES ( \'" + update.message.text + "\', \'1\')")
                #             conn.commit()
                #         adm_sessionslist.remove(session)
                #         t_answ = "Администратор добавлен: " + update.message.text
                #         update.message.reply_text(t_answ)

                if session[2] == "adm_del_cb":
                    if update.message.text == "Да":
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("DELETE FROM botusers WHERE u_id = \'" + g_id + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = "Администратор удалён: " + g_id
                        update.message.reply_text(t_answ)
                    if update.message.text == "Нет":
                        adm_sessionslist.remove(session)
                        t_answ = "Отменено."
                        update.message.reply_text(t_answ)

                if session[2] == "adm_rank_cb":
                    if update.message.text.isdigit():
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("UPDATE botusers SET u_privs = \'" + update.message.text + "\' WHERE u_id = \'" + g_id + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = "Ранг задан: " + update.message.text
                        update.message.reply_text(t_answ)
