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
                        # id | u_id | u_privs
                        cursor.execute("CREATE TABLE botusers ( \
                                        id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                                        u_id INT, \
                                        u_privs INT)")
                        cursor.execute("INSERT INTO botusers ( u_id, u_privs ) VALUES ( \'" + str(update.message.from_user.id) + "\', \'0\')")
                    cursor.execute("SELECT u_privs FROM botusers WHERE u_id = \'" + str(update.message.from_user.id) + "\'")
                    if cursor.rowcount == 0:
                        update.message.reply_text("Кто вы? Идите нахер, я вас не знаю!")
                    else:
                        privs = str(cursor.fetchone())[1:2]
                        check_adm(update, context, privs)
                conn.commit()

def check_adm(update, context, privs):
    """Check for admin privileges."""
    if int(privs) < 2:
        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE \'chat%\'")
                if cursor.rowcount != 0:
                    keyboard = []
                    ret = cursor.fetchall()
                    i = 0
                    for r in ret:
                        c_id = int(str(r)[6:][:-3].replace("_","-"))
                        c_info = context.bot.get_chat(c_id)
                        if c_info["type"] != "private":
                            if context.bot.get_chat_member(c_id, context.bot.get_me()["id"])["status"] == "administrator":
                                c_data = "checkadm" + privs + " " + str(c_id)
                                keyboard.append([InlineKeyboardButton(c_info["title"], callback_data=c_data)])
                                i += 1
                    if int(privs) < 1:
                        keyboard.append([InlineKeyboardButton("[Администраторы]", callback_data="admins")])
                    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('Чат:', reply_markup=reply_markup)

def admins_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Администраторы:")
    r_msg = ""
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u_id FROM botusers WHERE u_privs = '1'")
            if cursor.rowcount != 0:
                ret = cursor.fetchall()
                for r in ret:
                    r_msg += "\n" + str(r)[1:-2]
    keyboard = []
    keyboard.append([InlineKeyboardButton("Добавить", callback_data="adm_add")])
    if r_msg == "":
        r_msg += "(пусто)"
    else:
        keyboard.append([InlineKeyboardButton("Удалить", callback_data="adm_del")])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(r_msg, reply_markup=reply_markup)

def adm_add_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.message.text)
    query.message.reply_text("Добавить:")
    session = [query.from_user.id, "adm", "adm_add_cb"]
    adm_sessionslist.append(session)

def adm_del_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.message.text)
    query.message.reply_text("Удалить:")
    session = [query.from_user.id, "adm", "adm_del_cb"]
    adm_sessionslist.append(session)

def checkadm_cb(update, context):
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
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_f_times_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новое количество сообщений:")

def af_f_secs_cb(update, context):
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_f_secs_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новый интервал времени, сек:")

def af_b_secs_cb(update, context):
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    global adm_sessionslist
    session = [query.from_user.id, g_id, "af_b_secs_cb"]
    adm_sessionslist.append(session)
    query.edit_message_text(text="Новая длительность блокировки, сек (>30):")

def cancel_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.message.text)
    query.message.reply_text(text="Отменено.")

def check_sessions(update, context):
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

                if session[2] == "adm_add_cb":
                    if update.message.text.isdigit(): #todo: additional check
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("INSERT INTO botusers ( u_id, u_privs ) VALUES ( \'" + update.message.text + "\', \'1\')")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = "Администратор добавлен: " + update.message.text
                        update.message.reply_text(t_answ)

                if session[2] == "adm_del_cb":
                    if update.message.text.isdigit(): #todo: additional check
                        pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                        pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
                        with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("DELETE FROM botusers WHERE u_id = \'" + update.message.text + "\'")
                            conn.commit()
                        adm_sessionslist.remove(session)
                        t_answ = "Администратор удалён: " + update.message.text
                        update.message.reply_text(t_answ)
